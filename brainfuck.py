#!/usr/bin/env python3
"""brainfuck 解释器：玩具语言，小巧实现。

行为约定（README 同步说明）：
- 纸带默认 30000 字节（经典大小），可用 --tape-size 修改。
- 单元格 0-255 回绕：256 次 + 回到 0；0 再 - 回到 255。
- 括号预先配对：未配对的 [ 或 ] 直接报错，不会卡死。
- , 从 stdin 按字节读；EOF 时单元格置 0（经典约定之一）。
- 无限循环由 --max-steps 步数上限兜底。
"""

import argparse
import sys

COMMANDS = set("><+-.,[]")


def build_bracket_map(code):
    """预配对括号。返回 {左: 右, 右: 左}；未配对则抛 ValueError。"""
    stack = []
    pairs = {}
    for i, ch in enumerate(code):
        if ch == "[":
            stack.append(i)
        elif ch == "]":
            if not stack:
                raise ValueError(f"未配对的 ']'（位置 {i}）")
            j = stack.pop()
            pairs[j] = i
            pairs[i] = j
    if stack:
        raise ValueError(f"未配对的 '['（位置 {stack[-1]}）")
    return pairs


def run(code, tape_size=30000, max_steps=10_000_000, stdin_data=b""):
    """执行 brainfuck 程序。返回输出字节串。"""
    code = "".join(ch for ch in code if ch in COMMANDS)
    pairs = build_bracket_map(code)
    tape = bytearray(tape_size)
    ptr = 0
    pc = 0
    steps = 0
    out = bytearray()
    stdin_pos = 0
    n = len(code)
    while pc < n:
        steps += 1
        if steps > max_steps:
            raise RuntimeError(f"超过最大步数 {max_steps}，疑似无限循环")
        ch = code[pc]
        if ch == ">":
            ptr += 1
            if ptr >= tape_size:
                raise RuntimeError(f"纸带指针越界（>{tape_size - 1}）")
        elif ch == "<":
            ptr -= 1
            if ptr < 0:
                raise RuntimeError("纸带指针越界（<0）")
        elif ch == "+":
            tape[ptr] = (tape[ptr] + 1) % 256
        elif ch == "-":
            tape[ptr] = (tape[ptr] - 1) % 256
        elif ch == ".":
            out.append(tape[ptr])
        elif ch == ",":
            if stdin_pos < len(stdin_data):
                tape[ptr] = stdin_data[stdin_pos]
                stdin_pos += 1
            else:
                tape[ptr] = 0
        elif ch == "[":
            if tape[ptr] == 0:
                pc = pairs[pc]
        elif ch == "]":
            if tape[ptr] != 0:
                pc = pairs[pc]
        pc += 1
    return bytes(out)


def read_program(args):
    if args.program is not None:
        return args.program
    if args.stdin:
        return sys.stdin.read()
    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as f:
                return f.read()
        except OSError as e:
            print(f"error: 无法读取文件 {args.file}：{e}", file=sys.stderr)
            sys.exit(2)
    print("error: 请指定程序文件、-e 或 --stdin", file=sys.stderr)
    sys.exit(2)


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="brainfuck",
        description="Brainfuck 解释器（玩具实现，纯标准库）",
    )
    p.add_argument("file", nargs="?", help="brainfuck 程序文件")
    p.add_argument("-e", "--program", dest="program", help="直接给出程序文本")
    p.add_argument("--stdin", action="store_true", help="从 stdin 读取程序")
    p.add_argument("--tape-size", type=int, default=30000, help="纸带大小（默认 30000）")
    p.add_argument("--max-steps", type=int, default=10_000_000, help="最大执行步数（默认 10000000）")
    args = p.parse_args(argv)

    if args.tape_size <= 0:
        print("error: --tape-size 必须是正整数", file=sys.stderr)
        sys.exit(2)

    code = read_program(args)
    stdin_data = b""
    # 只有程序里真的有 , 指令时才读 stdin，避免无输入环境下 read() 永久阻塞
    if "," in code and not sys.stdin.isatty():
        if args.program is not None or args.file:
            try:
                stdin_data = sys.stdin.buffer.read()
            except OSError:
                stdin_data = b""
    try:
        out = run(code, tape_size=args.tape_size, max_steps=args.max_steps, stdin_data=stdin_data)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
    sys.stdout.buffer.write(out)
    sys.stdout.buffer.flush()


if __name__ == "__main__":
    main()
