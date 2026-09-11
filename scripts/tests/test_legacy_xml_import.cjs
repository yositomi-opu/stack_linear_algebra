// Exercise the production Maxima import helpers without starting a browser.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '../..');
const source = fs.readFileSync(path.join(root, 'app/mcq-webapp/app.js'), 'utf8');
const context = vm.createContext({});
const names = ['stripMaximaComments', 'splitMaximaStatements', 'parseMaximaAssignment',
  'managedAssignments', 'extractLanguageAssociation', 'parseMaximaValue',
  'skipWhitespace', 'skipBalanced', 'typedFromAst', 'optionPatternData', 'appendImportedRows',
  'csvValueType'];
const functions = names.map(name => {
  const match = source.match(new RegExp(`^function ${name}\\([^]*?^}`, 'm'));
  assert.ok(match, name);
  return match[0];
}).join('\n');
vm.runInContext(`const LANGS = ['en','ja','fr','it','de','pt','zh','ko','ru','sv'];
function baseLang() { return 'ja'; }
${functions}`, context);
function imported(code, truth = 'C') {
  context.code = code;
  context.truth = truth;
  return JSON.parse(vm.runInContext(`JSON.stringify((() => {
    const assignments = splitMaximaStatements(stripMaximaComments(code)).map(parseMaximaAssignment).filter(Boolean);
    const options = managedAssignments(assignments, new RegExp('^%__' + truth + 'optL?(\\\\d+)L?$'), ['ja','en']);
    const messages = managedAssignments(assignments, new RegExp('^%__' + truth + 'msg(\\\\d+)L?$'), ['ja','en']);
    const data = optionPatternData(options, 'ja');
    const rows = [];
    data.patterns.forEach((_, i) => appendImportedRows(rows, String(i+1).padStart(2,'0'), truth, i, data, messages, ['ja','en']));
    return rows;
  })())`, context));
}
function assertList(row, expr, lang = 'ja') {
  assert.equal(row[`choice_type_${lang}`], 'cas');
  assert.equal(row[`choice_list_expr_${lang}`], true);
  assert.equal(row[`choice_${lang}`], expr);
  assert.equal(context.csvValueType(row[`choice_type_${lang}`], row[`choice_list_expr_${lang}`]), 'cas_list');
}
for (const name of ['%__Copt1L', '%__CoptL1', '%__CoptL1L']) {
  for (const expr of ['[aa, bb]', '[aa]', 'CL1', 'map(tex2, [aa, bb])', 'ListAL[1]', '[[aa,bb],[cc,dd]]', '[]']) {
    const rows = imported(`${name}:${expr};`);
    assert.equal(rows.length, 1, `${name}:${expr}`);
    assertList(rows[0], expr);
  }
}
const multilingual = imported('%__CoptL1L:[["ja", [aa, bb]], ["en", map(tex2, [aa, bb])]]; %__Cmsg1L:[["ja", "説明"], ["en", "Feedback"]];');
assert.equal(multilingual.length, 1);
assertList(multilingual[0], '[aa, bb]');
assertList(multilingual[0], 'map(tex2, [aa, bb])', 'en');
assert.equal(multilingual[0].feedback_ja, '説明');
assert.equal(multilingual[0].feedback_type_ja, 'text');
const xml = fs.readFileSync(path.join(root, 'app/mcq-webapp/samples/001.mcq_sample01.xml'), 'utf8');
const vars = xml.match(/<questionvariables>\s*<text><!\[CDATA\[([^]*?)\]\]><\/text>/)[1];
assert.equal(imported(vars).length, 4, 'legacy randomized XML retains four patterns');
let count = 0;
for (const file of fs.readdirSync(path.join(root, '001')).filter(f => f.endsWith('.txt'))) {
  const code = fs.readFileSync(path.join(root, '001', file), 'utf8');
  const assignments = context.splitMaximaStatements(context.stripMaximaComments(code)).map(context.parseMaximaAssignment).filter(Boolean);
  for (const truth of ['C','W']) {
    for (const assignment of assignments.filter(a => new RegExp(`^%__${truth}optL?\\d+L?$`).test(a.name))) {
      if (context.extractLanguageAssociation(assignment.expression)) continue;
      const rows = imported(assignment.raw, truth);
      assert.equal(rows.length, 1, file + ': ' + assignment.name);
      assertList(rows[0], assignment.expression);
      count++;
    }
  }
}
assert.ok(count > 0);
console.log(`Passed: list expressions, multilingual feedback, legacy XML, and ${count} direct option assignments from 001/*.txt`);
