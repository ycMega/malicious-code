const fs = require('fs');
const esprima = require('esprima');

// 从命令行获取文件名
const fileName = process.argv[2];

// 读取文件内容
fs.readFile(fileName, 'utf8', (err, jsCode) => {
    if (err) {
        console.error(`Error reading file: ${err.message}`);
        process.exit(1);
    }

    // console.log(`Reading file: ${fileName}`);

    // 移除数字中的下划线
    const cleanedCode = jsCode.replace(/(\d)_(?=\d)/g, '$1');

    try {
        // 生成 AST
        const ast = esprima.parseScript(cleanedCode, {
            tolerant: true,
            loc: true
        });

        // console.log('AST generated successfully.');
        console.log(JSON.stringify(ast, null, 2));
    } catch (parseError) {
        console.error(`Error parsing code: ${parseError.message}`);
        const lineNumber = parseError.lineNumber;
        const errorLine = cleanedCode.split('\n')[lineNumber - 1];
        console.error(`Error in line ${lineNumber}: ${errorLine}`);
    }
});