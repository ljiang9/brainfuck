# brainfuck

Brainfuck 解释器：玩具语言，小巧实现。纯 Python 标准库，零依赖。

## 快速开始

```bash
python3 -m brainfuck examples/hello.bf
# Hello World!

echo -n "abc" | python3 -m brainfuck -e ',[.,]'
# abc

echo '++++++++[>++++[>++>+++>+++>+<<<<-]>+>+>->>+[<]<-]>>.>---.+++++++..+++.>>.<-.<.+++.------.--------.>>+.>++.' | python3 -m brainfuck --stdin
# Hello World!
```

## 用法

```
brainfuck 程序文件.bf        # 运行文件
brainfuck -e '++.'            # 直接运行程序文本
brainfuck --stdin < prog.bf   # 从 stdin 读程序
brainfuck --tape-size 1000 prog.bf   # 自定义纸带大小
brainfuck --max-steps 1000 prog.bf   # 自定义步数上限
```

## 行为约定（诚实说明）

- **纸带**：默认 30000 字节（经典大小），指针越界报错退出。
- **单元格回绕**：0–255 循环。256 次 `+` 回到 0；0 再 `-` 回到 255。
- **括号预配对**：运行前先配对全部 `[` `]`；未配对的直接中文报错退出（exit 1），不会卡死。
- **`,` 输入**：从 stdin 按字节读；遇到 EOF 时单元格置 0（这是几种经典约定之一，本实现采用此种）。
- **无限循环兜底**：`--max-steps`（默认 10000000）步后强制终止并报错。
- **非指令字符**：注释，直接忽略。

## 已知局限

- 这是个玩具解释器：没有 JIT、没有优化，性能只够跑教学程序。
- `,` 的 EOF 置 0 是约定选择之一，其他实现可能置 -1（255）或不变。
- 只支持标准 8 指令；Brainfuck 方言扩展不在范围内。
