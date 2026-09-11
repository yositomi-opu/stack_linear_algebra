const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.resolve(__dirname, '../../app/mcq-webapp/app.js'), 'utf8');
const names = ['updateOptionLimit','choiceValueType','evaluatedChoiceCapacity','choiceEvaluationId',
  'patternChoiceCapacity','groupPatterns','normalizeTruth','correctCountChoices','nonNegativeInt',
  'generateFixedVariableBlock'];
const functions = names.map(name => {
  const match = source.match(new RegExp(`^function ${name}\\([^]*?^}`, 'm'));
  assert.ok(match, name);
  return match[0];
}).join('\n');
const state = { rows: [
  {pattern:'01',truth:'C',choice_ja:'CL',choice_type_ja:'cas',choice_list_expr_ja:true},
  {pattern:'01',truth:'W',choice_ja:'WL',choice_type_ja:'cas',choice_list_expr_ja:true},
], casEvaluation:{stale:false,expressions:{}}};
const el = {numOptions:{value:'6', max:'99', removeAttribute(key){delete this[key];}},
  requirePairs:{checked:false}, randomCorrect:{checked:true},correctCounts:{value:'0, 1, 2, 3, 4'},numCorrect:{value:'4'}};
const context = vm.createContext({state,el});
vm.runInContext(`function baseLang(){return 'ja';} function activeLangs(){return ['ja'];}
function baseVariableLines(n,counts){return [String(n), counts.join(',')];}
function appendFixedPattern(lines,truth,slot,pattern){lines.push(truth+slot);}
${functions}`, context);
context.updateOptionLimit();
assert.equal(el.numOptions.value,'6','import must not shrink 6 to 2 before evaluation');
assert.equal(el.numOptions.max,undefined,'unknown list length must not set a false upper bound');
state.casEvaluation.expressions = {'choice:0:ja':{ok:true,type:'list',length:4},'choice:1:ja':{ok:true,type:'list',length:13}};
context.updateOptionLimit();
assert.equal(el.numOptions.max,'17');
assert.equal(el.numOptions.value,'6');
let counts=context.correctCountChoices(Number(el.numOptions.value));
assert.doesNotThrow(()=>context.generateFixedVariableBlock(context.groupPatterns(),6,counts));
el.randomCorrect.checked=false;
assert.doesNotThrow(()=>context.generateFixedVariableBlock(context.groupPatterns(),6,context.correctCountChoices(6)));
el.numCorrect.value='5';
assert.throws(()=>context.generateFixedVariableBlock(context.groupPatterns(),6,context.correctCountChoices(6)),/正解選択肢が不足/);
assert.throws(()=>context.correctCountChoices(2),/正解数が選択肢数を超え/);
el.numOptions.value='18';
context.updateOptionLimit();
assert.equal(el.numOptions.value,'18','do not silently change an invalid explicit setting');
assert.throws(()=>context.generateFixedVariableBlock(context.groupPatterns(),18,[4]),/誤答選択肢が不足/);
state.casEvaluation.stale=true;
context.updateOptionLimit();
assert.equal(el.numOptions.max,undefined);
assert.equal(el.numOptions.value,'18');
console.log('Passed: unevaluated import preserves count; 4 correct + 13 wrong allow 0–4 correct among 6 options; invalid counts remain rejected.');
