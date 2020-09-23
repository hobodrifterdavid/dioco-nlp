import express from 'express';
import bodyParser from 'body-parser';
import got from 'got';
import compression from 'compression'
import * as fs from 'fs';

const app = express();
const port = 3000;

app.use(compression())

app.use(bodyParser.json({
  limit: '50mb'
}));

app.use(bodyParser.urlencoded({
  limit: '50mb',
  parameterLimit: 100000,
  extended: true 
}));

interface Sub {
    begin: number;
    end: number;
    text: string;
}

type LangCode_G = string;

type Subtitle_Tokens = Array<ud_single|ud_group>;

interface ud_single {
    
    form: string;
    pos: 
    // 17 Universal POS tags:
    'ADJ'|'ADP'|'ADV'|'AUX'|'NOUN'| 
    'PROPN'|'VERB'|'DET'|'SYM'|'INTJ'|
    'CCONJ'|'PUNCT'|'X'|'NUM'|'PART'|
    'PRON'|'SCONJ'|
    // Unknown text, either UDPipe returned nothing 
    // for this token, or simpleNLP identified it as
    // not whitespace and not punctuation:
    '_'|
    // Whitespace:
    'WS';
    index?: number;
    lemma?: string;
    xpos?: string;
    features?: any;
    pointer?: number;
    deprel?: string;
    translit?: string; // currently only Korean, Thai, Japanese (kana)
    pinyin?: Array<string>;
    tones?: Array<number>;
    freq?: number;
}

interface ud_group {
    form: string;
    pos: 'GROUP'
    members: Array<ud_single>;
    index?: number;
    translit?: string; // currently only Korean, Thai
    pinyin?: Array<string>;
    tones?: Array<number>;
    freq?: number;
}

function asFlatList(inputTokens: Subtitle_Tokens): Subtitle_Tokens {
    
    let outputTokens: Subtitle_Tokens = [];

    for(let token of inputTokens) {
        if(token.pos === 'GROUP') {
            outputTokens.concat([token, ...token.members]);
        }
        else {
            outputTokens.push(token);
        }
    }

    return outputTokens;
}

const lemmaFreqData = JSON.parse(fs.readFileSync('./lemmaRank.json', 'utf8'));

interface getNLP_9_ED {
    source: 'YOUTUBE'|'NETFLIX';
    tt_key: string;
    subs: [number,number,string][];
    sourceLangCode_G: string;
    numSubs: number;
}

app.post('/getNLP_9', async (req, res) => {

    let startTime_TOTAL = (new Date()).getTime();

    const req_data: getNLP_9_ED = req.body;

    // transform to an array of strings
    let subtitleText: Array<string> = req_data.subs.map((element: any[]) => element[2]);

    // Take out the RTL and LTR chars, the tokenisers don't like them.
    // Slightly random list from: https://www.w3schools.com/charsets/ref_utf_punctuation.asp
    // In Unicode, the LRM character is encoded at U+200E LEFT-TO-RIGHT MARK (HTML &#8206; · &lrm;).
    // In Unicode, the RLM character is encoded at U+200F RIGHT-TO-LEFT MARK (HTML &#8207; · &rlm;). 
    // 8234 LEFT-TO-RIGHT EMBEDDING
    // 8235 RIGHT-TO-LEFT EMBEDDING
    // 8236 POP DIRECTIONAL FORMATTING
    // 8237 LEFT-TO-RIGHT OVERRIDE
    // 8238 RIGHT-TO-LEFT OVERRIDE

    let removeList = [8206, 8207, 8234, 8235, 8236, 8237, 8238];
    subtitleText = subtitleText.map(subString => {
        return Array.from(subString)
                .filter(char => !removeList.includes(char.codePointAt(0) || 0 ) )
                .join('');
    });

    let startTime_UDPIPE = (new Date()).getTime();

    let {err, nlp_data} = await runUDPIPE(subtitleText, req_data.sourceLangCode_G, req_data);

    let tookTime_UDPIPE = (new Date()).getTime() - startTime_UDPIPE;

    let nice_subs: Subtitle_Tokens[] = [];

    if (nlp_data === null || err !== null) {
        if (err === 'NO_INPUT_SUBS') {
            console.log(`No input subs. subs.length: ${req_data.subs.length} source: ${req_data.source} tt_key: ${req_data.tt_key}`);
        }
        else if (err === 'MISSING_MODEL_ETC') {
            console.log(`No model for '${req_data.sourceLangCode_G}', using getSimpleNLP.`);
            nice_subs = subtitleText.map(sub => getSimpleNLP_Nice(sub));
        } else {
            console.log(`RES 401: Requested new data from NLP server, FAIL (${err}).`);
            return res.status(401).send();
        }
    } else {

        // Check Python code gave us what we need
        for(let sub of nlp_data) {
            for(let token of sub) {
                if(!token.pos) {
                    console.error(sub);
                }
                if(token.pos !== 'GROUP') {
                    // For single
                    if(!token.form) {
                        console.error(sub);
                    }
                }
                if(token.pos === 'GROUP') {
                    // For group
                    if(!token.form || !token.members.length) {
                        console.error(sub);
                    }
                }
            }
        }

        nice_subs = 
            nlp_data
                .map((sub, i) => reconstructSpaces(sub, subtitleText[i]))
                .map(sub => tryToUnnest(sub, req_data.sourceLangCode_G))
                .map(sub => fixUdpipeCommonModelErrors(sub, req_data.sourceLangCode_G))
                // .map(sub => fix_deprel_indexes(sub))
                .map(sub => clearIndexes(sub, req_data.sourceLangCode_G))
                .map(sub => clearLemmas(sub));
    }

    nice_subs = nice_subs.map(sub => addTokenFrequencies(sub, req_data.sourceLangCode_G));

    // on FE:
    // const compounds = makeCompounds(nice_subs);
/*
    // for testing

    let shown: any = {};
    
    for(let sub of nice_subs) {
        for(let token of sub) {
            if(shown[token.form] === undefined) {
                if(token.pos === 'GROUP') {
                    console.log(`F `,token.form);
                    console.log(`L GROUP`);
                    console.log(`P `,token.pos);
                }
                else {
                    console.log(`F `, token.form);
                    console.log(`L `, token.lemma);
                    console.log(`P `, token.pos);
                    if(token.xpos) {
                        console.log(`X `, token.xpos)
                    }
                }
                shown[token.form] = true;
            }
        }
    }
*/

    let tookTime_TOTAL = (new Date()).getTime() - startTime_TOTAL;

    if (tookTime_TOTAL < 10000) {
        console.log(`runUDPIPE took ${tookTime_UDPIPE} ms, TOTAL ${tookTime_TOTAL}, ${req_data.source} data length: ${JSON.stringify(req_data).length}, lang: ${req_data.sourceLangCode_G}`)
    }
    else {
        console.error(`runUDPIPE took ${tookTime_UDPIPE} ms, TOTAL ${tookTime_TOTAL}, ${req_data.source} data length: ${JSON.stringify(req_data).length}, lang: ${req_data.sourceLangCode_G}`);
    }
    
    console.log(`RES 200`);

    interface getNLP_9_RV {
        subtitlesNLP: Subtitle_Tokens[];
        // compounds: compounds,
        haveWordFrequency: boolean;
    }

    let rv:getNLP_9_RV = {   
        subtitlesNLP: nice_subs,
        // compounds: compounds,
        haveWordFrequency: !!lemmaFreqData[req_data.sourceLangCode_G]
    }
    return res.status(200).send(rv);

});

/*
function fix_deprel_indexes(sub_tokens: Subtitle_Tokens): Subtitle_Tokens {

    // UDPIPE Indexes start at 1
    // Ha!

    for(let token of sub_tokens) {
        if(token.pointer !== undefined) {
            // This token is trying to point to another token

            let lowestFound: false | number = false;

            for(let i = 0; i < sub_tokens.length; i++) {
                // Find the token it's trying to point to

                let this_sub_token = sub_tokens[i];
                
                if( this_sub_token.index !== undefined ) {
                    if(this_sub_token.index <= token.pointer) {
                        lowestFound = i;
                    }
                }
            }
            if(lowestFound !== false) {
                token.pointer = lowestFound;
            }
        }
    }

    return sub_tokens;
}

function makeCompounds(nice_subs: Subtitle_Tokens_Nice[]) {

    let compounds_master: any = {};

    for(let i = 0; i < nice_subs.length; i++) {
        // For each sub

        let compounds_sub: any = [];

        let nice_sub = nice_subs[i];

        let heads: any = {};

        for(let j = 0; j < nice_sub.length; j++) {
            // For each token
            let token = nice_sub[j];            

            if(token.deprel && token.deprel.includes('compound') && token.pointer) {
                // Stuff being pointed to
                let pointedTo = token.pointer;
                let pointedFrom = j;

                if(heads[pointedTo] === undefined) {
                    heads[pointedTo] = [];
                }

                if(!heads[pointedTo].includes(pointedFrom)) {
                    heads[pointedTo].push(pointedFrom);
                }
            }
        }

        // Object.keys always returns strings?
        for(let head of Object.keys(heads).map(key => parseInt(key))) {
            
            compounds_sub.push([head, ...heads[head]]);
        }
        
        // All tokens for that sub processed

        if(compounds_sub.length > 0) {
            compounds_master[i] = compounds_sub;
        }
    }

    return compounds_master;
}
*/

function addTokenFrequencies(subTokens: Subtitle_Tokens, sourceLangCode_G: string): Subtitle_Tokens {

    let flatList = asFlatList(subTokens);

    for (let token of flatList) {
        // Not for WS or PUNCT
        if(token.pos !== 'PUNCT' && token.pos !== 'WS') {

            if(token.pos !== 'GROUP' && token.lemma) {
                // There is a lemma, is it in the list?
                if (lemmaFreqData[sourceLangCode_G] && lemmaFreqData[sourceLangCode_G][token.lemma.toLowerCase()] === undefined) {
                    // No, it's not, remove it.
                    delete token.lemma;
                }
            }

            let textForFreq = '';

            if(token.pos !== 'GROUP' && token.lemma) { 
                textForFreq = token.lemma.toLowerCase(); 
            }
            else { 
                textForFreq = token.form.toLowerCase(); 
            }
            
            // const pos = word[2]; // take any pos tags mentioned for the lemma
            if (lemmaFreqData[sourceLangCode_G] && lemmaFreqData[sourceLangCode_G][textForFreq] !== undefined) {
                token.freq = lemmaFreqData[sourceLangCode_G][textForFreq];
            }
        }
    }
    return subTokens;
}

async function runUDPIPE(subsToSend: Array<string>, langCode_G: LangCode_G, req_data: any): Promise<{ err: string | null; nlp_data: Subtitle_Tokens[] | null }> {

    // console.log('processAndTokenizeSubs, req_data: ', req_data);

    // req_data is used when logging errors

    if (!subsToSend || subsToSend.length === 0) return {err: 'NO_INPUT_SUBS', nlp_data: null};

    let dataToSend = {subtitles: subsToSend, lang: langCode_G};

    // console.log('###', JSON.stringify(dataToSend));

    try {

        let errorEnum: string | null = null;
        let json: any = null;

        // got('http://unix:/var/run/docker.sock:/containers/json');

        try {
            const {body}: any = await got.post('http://unix:/root/nlp_server/python/nlp_app.sock:/api/nlp/', {
                json: dataToSend,
                responseType: 'json'
            });

            // console.log('AAA', body);
            json = body;

        } catch (error) {
            // Array of errors here: error.response.body.errors
            if (error.response.body.errors.includes('No Model Found')) {
                // console.log(`runUDPIPE(): No Model for ${langCode_G}, req_data: `, req_data);
                errorEnum = 'MISSING_MODEL_ETC';
            } else {
                console.error(`runUDPIPE(): unknown request fail: ${error.response.body}, req_data: `, req_data);
                errorEnum = 'TOKENS_SERVER_DOWN';
            }
        }

        if (errorEnum || !json) {
            return {err: errorEnum, nlp_data: null};
        }

        if (!json.subtitles || !json.subtitles.length) {
            // console.log(`runUDPIPE(): !json.subtitles || !json.subtitles.length, lang ${langCode_G}, json: `, json);
            return {err: 'NO_SUBS_RETURNED', nlp_data: null}
        } else {
            return {err: null, nlp_data: json.subtitles};
        }
    } catch (e) {
        console.error(`runUDPIPE() e: ${e}, req_data: `, req_data);
        return {err: 'TOKENS_SERVER_DOWN', nlp_data: null}
    }
};

// - reconstructs space-character tokens
// add white-space (non-word) tokens into a list of udpipe tokens
// reason: udpipe doesn't return white space info in a consistent way
// this function ensures that the resulting tokens together produce text equivalent to the given subtitleText
function reconstructSpaces(subtitleTokens: Subtitle_Tokens, subtitleText: string): Subtitle_Tokens {

    // normalise whitespace
    // Actually no
    // let subtitleText_copy = subtitleText.split('\n').join(' ').replace(/  +/g, ' ');

    function normalizeWhitespace(input:string): string {
        return input.split('\n').join(' ').replace(/  +/g, ' ');
    }

    // new output
    let outputTokens = [];

    try {
        outputTokens = doPressups(subtitleTokens, subtitleText);
    }
    catch {
        // Were you born a fat, slimy, scumbag puke piece o' shit, Private Pyle, or did you have to work on it?
        subtitleText = normalizeWhitespace(subtitleText);
        for(let token of subtitleTokens) {
            token.form = normalizeWhitespace(token.form);
        }
        outputTokens = doPressups(subtitleTokens, subtitleText);
    }

    function doPressups(subtitleTokens: Subtitle_Tokens, subtitleText: string): Subtitle_Tokens {

        let outputTokens_inner = [];

        for (let token of subtitleTokens) {

            let tokenIndex = subtitleText.indexOf(token.form);

            if (tokenIndex === -1) { 
                // if token not found in subtitleText, throw an error
/*
                console.error(`reconstructSpaces(): token not found in subtitleText.`);
                console.error(`Problem token: '${token.form}'`);
                console.error(`Subtitle tokens: '${JSON.stringify(subtitleTokens.map(token => token.form))}'`);
                console.error(`subtitleText: ${subtitleText}`);
*/
                // Holy Jesus! What is that? What the fuck is that? WHAT IS THAT, PRIVATE PYLE?
                // Sir, a jelly doughnut, sir!
                throw new Error('tokenizeSubs : reconstructSpaces: token not found');
            }
            else if (tokenIndex > 0) { 
                // if token found, but not at start, add another white-space token in between
                // add intermediate token
                let whiteSpaceText = subtitleText.slice(0, tokenIndex);
                if (whiteSpaceText.trim().length > 0) {
                    // We skipped some chars, something wierd is going on.
                    throw new Error('tokenizeSubs : reconstructSpaces: found non-space characters not present as tokens: "' + whiteSpaceText + '" in ' + subtitleText);
                }
                let newToken: ud_single = { form: whiteSpaceText, pos: 'WS' }

                outputTokens_inner.push(newToken); // white space - no lemma or POS tag
            }
            subtitleText = subtitleText.slice(tokenIndex + token.form.length);
            outputTokens_inner.push(token);
        }

        // add potential space after last found token
        if (subtitleText) {
            // throw error if anything remains that is not a space character
            if (subtitleText.trim().length > 0) {
                throw new Error('tokenizeSubs : reconstructSpaces: found non-space characters not present as tokens: "' + subtitleText + '" in ' + subtitleText);
            }
            let newToken: ud_single = { form: subtitleText, pos: 'WS' }
            outputTokens_inner.push(newToken);  // white space - no lemma or POS tag
        }

        return outputTokens_inner;

    }

    let testString = '';
    for (let token of outputTokens) {
        testString += token.form;
    }

    if(testString !== subtitleText) {
        console.error(`testString !== subtitleText: [${testString}] [${subtitleText}]`);
    }

    return outputTokens;
}

// unpack A5 format
// (some tokens contain array of sub-lemmas, so we flatten that out here)
// we also do some small corrections here
function tryToUnnest(subtitleTokens: Subtitle_Tokens, langCode_G: string): Subtitle_Tokens {

    let resultTokens: Subtitle_Tokens = [];

    for (let token of subtitleTokens) {

        if (token.pos !== 'GROUP') {
            // Can't unnest if not a GROUP
            resultTokens.push(token);
            continue;
        }

        let group_token = token;

        if (group_token.members.map(singleItem => singleItem.form).join('') === group_token.form) {
            // Can uunest
            // if when member's forms are combined, they make group form - return them individually
            for (let singleItem of group_token.members) {
                resultTokens.push(singleItem);
            }
        }
        else if(langCode_G.startsWith('pt') && group_token.form.includes('-') && group_token.members.length == 2 && group_token.members[0].pos == 'VERB') {
        // {"form":"Cuida-te","index":"2-3","members":
        //      [{"feats":{"Gender":"Fem","Number":"Sing","VerbForm":"Part"},"form":"Cuida","index":2,"lemma":"cuidar","pos":"VERB"},
        //       {"feats":{"Case":"Acc","Gender":"Masc","Number":"Sing","Person":"2","PronType":"Prs"},"form":"te","index":3,"lemma":"tu","pos":"PRON"}],
        //  "pos":"GROUP"}
            let first: ud_single = group_token.members[0];
            first.form = group_token.form.split('-')[0];
            resultTokens.push(first);

            let second: ud_single = { form: '-', pos: 'PUNCT' };
            resultTokens.push(second);

            let third: ud_single = group_token.members[1];
            third.form = group_token.form.split('-')[1];
            resultTokens.push(third);
        }
        else {
            // Cannot unnest
            resultTokens.push(group_token);
            // for testing:
            // console.error(JSON.stringify(group_token));
        }
    }

    return resultTokens;
};

// some udpipe language models occasionally group words with '...' and '-', among other punctuation.
// these words don't have lemma, so here we just split them into 2 tokens.
// e.g. 'here...' will be split into 'here' and '...' tokens
function fixUdpipeCommonModelErrors(tokenArray: Subtitle_Tokens, lang_G: string): Subtitle_Tokens {

    // List of stuff to check

    // Thai model can return no lemma (_)
    // fix for german, where it returns multiple possible lemmas delimited by "|"
    // members of groups have forms that don't add up to group form
    
    let resultTokens = [];

    for (let token of tokenArray) {

/*
        if(token.form.length > 1 && token.form[0] === token.form[token.form.length -1]) {
            console.error(`XXXXXXXXXXXXXXX: `, JSON.stringify(token));
            
            const sa = Array.from(token.form);
            if(sa) {
                for(let char of sa) {
                    console.log(char.charCodeAt(0));
                }
            }
        }

        if(token.lemma && token.lemma.length > 1 && token.lemma && token.lemma[0] === token.lemma[token.form.length -1]) {
            console.error(`ZZZZZZZZZZZZZZZ: `, JSON.stringify(token));
            
            const sa = Array.from(token.lemma);
            if(sa) {
                for(let char of sa) {
                    console.log(char.charCodeAt(0));
                }
            }
        }

        if(token.form === '') {
            // discard tokens with no actual text (to click)
            console.error(`### Discarding token, no form: `, JSON.stringify(token));
            continue;
        }
*/
        ////////// Fixes for German.. but they might appear elsewhere..

        // Only for non-group tokens

        if (token.pos !== 'GROUP') {

            if (lang_G !== 'hi' && token.lemma && token.lemma.indexOf('|') > -1) {
                // fix for german, where it returns multiple possible lemmas delimited by "|"
                // console.error(`### | in lemma: `, JSON.stringify(token));
                token.lemma = token.lemma.substring(0, token.lemma.indexOf('|'));
            }

            // Fix this is German model: form:'gibst' lemma:'-' pos:'VERB'
            if (token.form !== '-' && token.lemma === '-' && token.pos !== 'PUNCT') {
                // console.error(`### - for lemma: `, JSON.stringify(token));
                delete token.lemma;
            }

            // Fix this is German model: 'ersten'    'NULL'      'ADJ'
            if (token.form !== 'NULL' && token.lemma === 'NULL') {
                // console.error(`### NULL for lemma: `, JSON.stringify(token));
                delete token.lemma;
            }

            // Fix this is German model:
            if (token.form !== 'unknown' && token.lemma === 'unknown') {
                // console.error(`### unknown for lemma: `, JSON.stringify(token));
                delete token.lemma;
            }

            // Also this one but eh..
            // 'wär's'     'wär's'     'PROPN'

            if(lang_G === 'fi' && token.lemma?.includes('#')) {
                token.lemma = token.lemma.replace('#','');
            }

            if(lang_G === 'hu' && token.lemma?.includes('+')) {
                token.lemma = token.lemma.replace('+','');
            }
        }

        //////////

        if (token.pos !== 'GROUP') {

            for(let returnedToken of cleanPunct(token)) {

                // Another fix.
                // Sometimes numbers aren't marked as numbers.
                if( returnedToken.pos !== 'PROPN' && !isNaN(parseInt(returnedToken.form)) ) {
                    // Something that at least starts with a number
                    let newToken: ud_single = {
                        form: returnedToken.form,
                        pos: 'NUM'
                    }
                    resultTokens.push(newToken);
                }
                else {
                    resultTokens.push(returnedToken);
                }
            }

        }
        else {
            resultTokens.push(token);
        }
    }
    return resultTokens;
}

function cleanPunct(passedToken: ud_single): ud_single[] {

    const charsToRemove = ['...','..','.','♪','~unknown~',`!`,`-`, `“`, `”`, '~_~', `„`, `~-~`, '[', ']', '?', ',', '(', ')',
    // New finds
    `'`,
    '#',
    '&',
    '´',
    '`',
    '’',
    ':',
    '+',
    '=',
    '>',
    '<',
    '@',
    '%',
    '§',
    '$',
    '°',
    '©',

    '）', //ja
    '！',
    ':',
    '？',
    ' ',
    '〜',
    '　',
    '―',
    '」',
    '〉',
    '〈',
    '､',
    '「',
    '/',
    '（',
    '·',
    '♯',
    '／',
    '\\',
    '•',
    '≠',
    '↓',
    '＆',
    ' ',
    '＂',
    '〟',
    '‟',
    '＞',
    ';',
    '＋',
    '~',
    '♡',
    '±',

    '≈',
    
    // Arabic
    `؟`,
    `،`,
    // Spanish
    `¿`,
    // Some RTL Hebrew ones:
        `…`, 
        `׃`,
        `׀`,
        `־`,
        `״`, 
        `"`,
    // Japanese:
        '･',
        '—',
        '〞',
        '･･･',
        '～',
    // Russian
        '«',
        '»',
    // Chinese
    // https://en.wikipedia.org/wiki/Chinese_punctuation
        '，',
        '！',
        '？',
        '；',
        '：',
        '（',
        '）',
        '［',
        '］',
        '【',
        '】',
        '。',
        // European quotation marks same
        '『',
        '』',
        '「',
        '」',
        '﹁',
        '﹂',
        '、',
        '‧',
        '《',
        '》',
        '〈',
        '〉',
        '⋯',
        '…',
        '——',
        '—',
        '～',
    // Hindi
        '|' // Full stop
    ];

    // This code seperates '-' or '...' into seperate tokens.
    if (passedToken.pos === 'PUNCT') {
        return [passedToken];
    }

    let tokensBefore: ud_single[] = [];
    let tokensAfter: ud_single[] = [];

    for(let i = 0; i < 2; i++) {
        // Run twice

        // search for chars to remove in passedToken
        for (let toRemove of charsToRemove) {
            if (passedToken.form.length >= toRemove.length && passedToken.form.startsWith(toRemove)) {
                // if text starts with char to remove, add separate tokens
                let newToken: ud_single = {
                    form: toRemove,
                    pos: 'PUNCT'
                }
                tokensBefore.push(newToken);

                // console.log(`###`,JSON.stringify(newToken));

                passedToken.form = passedToken.form.slice(toRemove.length);

                // Also clean lemma:
                if(passedToken.lemma !== undefined && passedToken.lemma.startsWith(toRemove)) {
                    passedToken.lemma = passedToken.lemma.slice(toRemove.length);
                }
            }
            if (passedToken.form.length > toRemove.length && passedToken.form.endsWith(toRemove)) {
                // if text ends with char to remove, add separate tokens
                passedToken.form = passedToken.form.slice(0,passedToken.form.length - toRemove.length);

                // Also clean lemma:
                if(passedToken.lemma !== undefined && passedToken.lemma.endsWith(toRemove)) {
                    passedToken.lemma = passedToken.lemma.slice(0,passedToken.lemma.length - toRemove.length);
                }

                let newToken: ud_single = {
                    form: toRemove,
                    pos: 'PUNCT'
                }

                tokensAfter.unshift(newToken);

                // console.log(`###`,JSON.stringify(newToken));
            }
        }
    }

    // search for chars to remove in passedToken lemma only
    for (let toRemove of charsToRemove) {
        if (passedToken.lemma && passedToken.lemma.length >= toRemove.length && passedToken.lemma.startsWith(toRemove)) {
            
            passedToken.lemma = passedToken.lemma.slice(toRemove.length);

        }
        if (passedToken.lemma && passedToken.lemma.length > toRemove.length && passedToken.lemma.endsWith(toRemove)) {

            passedToken.lemma = passedToken.lemma.slice(0,passedToken.lemma.length - toRemove.length);

        }
    }

    if(passedToken.lemma?.length === 0) {
        delete passedToken.lemma;
    }

    if(passedToken.form.trim().length === 0) {
        // We trimmed it down to WS only
        passedToken.pos = 'WS';
        delete passedToken.lemma;
    }

    // Thai tokeniser doesn't tag PUNCT, so need this stuff..
    // None of the original token is left.
    if(passedToken.form.length === 0) {
        return [...tokensBefore, ...tokensAfter];
    }

    return [...tokensBefore, passedToken, ...tokensAfter];
}

function clearIndexes(tokenArray: Subtitle_Tokens, langCode_G: LangCode_G): Subtitle_Tokens {

    // ["Bob", "bob", "PROPN", "NNP", "Number=Sing", "6", "nmod:poss", ""]
    //  0      1      2        3      4              5    6            7

    /*
    ID: Word index, integer starting at 1 for each new sentence; may be a range for multiword tokens; may be a decimal number for empty nodes (decimal numbers can be lower than 1 but must be greater than 0).
    FORM: Word form or punctuation symbol.
    LEMMA: Lemma or stem of word form.
    UPOS: Universal part-of-speech tag.
    XPOS: Language-specific part-of-speech tag; underscore if not available.
    FEATS: List of morphological features from the universal feature inventory or from a defined language-specific extension; underscore if not available.
    HEAD: Head of the current word, which is either a value of ID or zero (0).
    DEPREL: Universal dependency relation to the HEAD (root iff HEAD = 0) or a defined language-specific subtype of one.
    DEPS: Enhanced dependency graph in the form of a list of head-deprel pairs.
    MISC: Any other annotation.
    */

    let niceTokens = [];
  
    for(let token of tokenArray) {

        if(token.index !== undefined) { delete token.index; }

        niceTokens.push(token);
    }

    return niceTokens;
}

function clearLemmas(tokenArray: Subtitle_Tokens): Subtitle_Tokens {

    // Remove lemmas for punctuation

    let niceTokens = [];
  
    for(let token of tokenArray) {

        if(token.pos === 'PUNCT' && token.lemma !== undefined) { 
            delete token.lemma; 
        }

        // Should never be set for whitespace, but just in case..
        if(token.pos === 'WS' && token.lemma !== undefined) { 
            delete token.lemma; 
        }

        niceTokens.push(token);
    }

    return niceTokens;
}

/*
 * Tiny tokenizer
 *
 * - Accepts a subject string and an object of regular expressions for parsing
 * - Returns an array of token objects
 *
 * tokenize('this is text.', { word:/\w+/, whitespace:/\s+/, punctuation:/[^\w\s]/ }, 'invalid');
 * result => [{ token="this", type="word" },{ token=" ", type="whitespace" }, Object { token="is", type="word" }, ... ]
 *
 */
function tokenize ( s: string, parsers: any, deftok: any ) {
var m, r, l, t, tokens = [];
while ( s ) {
    t = null;
    m = s.length;
    for ( var key in parsers ) {
    r = parsers[ key ].exec( s );
    // try to choose the best match if there are several
    // where "best" is the closest to the current starting point
    if ( r && ( r.index < m ) ) {
        t = {
        token: r[ 0 ],
        type: key,
        matches: r.slice( 1 )
        }
        m = r.index;
    }
    }
    if ( m ) {
    // there is text between last token and currently 
    // matched token - push that out as default or "unknown"
    tokens.push({
        token : s.substr( 0, m ),
        type  : deftok || 'unknown'
    });
    }
    if ( t ) {
    // push current token onto sequence
    tokens.push( t ); 
    }
    s = s.substr( m + (t ? t.token.length : 0) );
}
return tokens;
}

// tokenize subs in a simple way
function getSimpleNLP_Nice(text: string): Subtitle_Tokens {

    let result = tokenize(text, { word:/\w+/, whitespace:/\s+/, punctuation:/[^\w\s]/ }, 'invalid');

    let niceTokens: Subtitle_Tokens = result.map(outputToken => {
        
        let form = <string>outputToken.token;
        let pos: '_'|'WS'|'PUNCT';

        if(outputToken.type === 'word') { pos = '_'; }
        else if(outputToken.type === 'whitespace') { pos = 'WS'; }
        else if(outputToken.type === 'punctuation') { pos = 'PUNCT'; }
        else { pos = 'PUNCT'; }

        return { form: form, pos: pos };

    });

    return niceTokens;
}

app.listen(port, () => console.log(`Example app listening at http://localhost:${port}`));
