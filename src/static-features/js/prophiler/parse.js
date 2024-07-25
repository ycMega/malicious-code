// 在AST中寻找长字符串

const esprima = require('esprima');
const fs = require('fs');

const code = fs.readFileSync(process.argv[2], 'utf8');
const ast = esprima.parseScript(code);

function findDecodingRoutines(node, longStringLength) {
    let count = 0;
    if (node.type === 'ForStatement' || node.type === 'WhileStatement') {
        const body = node.body.body;
        for (let i = 0; i < body.length; i++) {
            if (body[i].type === 'VariableDeclaration') {
                const declarations = body[i].declarations;
                for (let j = 0; j < declarations.length; j++) {
                    if (declarations[j].init && declarations[j].init.type === 'Literal' &&
                        typeof declarations[j].init.value === 'string' &&
                        declarations[j].init.value.length > longStringLength) {
                        count += 1;
                    }
                }
            }
        }
    }
    for (let key in node) {
        if (node.hasOwnProperty(key)) {
            const child = node[key];
            if (typeof child === 'object' && child !== null) {
                count += findDecodingRoutines(child, longStringLength);
            }
        }
    }
    return count;
}

const count = findDecodingRoutines(ast, 10); // Assuming "long" string length as 10
console.log(JSON.stringify({count}));