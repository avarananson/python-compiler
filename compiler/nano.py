# compiler
import argparse
import os
from lexer import Lexer
from parser import Parser
from interpreter import Interpreter
from compiler import Compile
from componenets import TokConsts

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='File to run')
    parser.add_argument('-sim', dest='sim', action='store_true',help='Simulate it')
    parser.add_argument('-compile', dest='compile', action='store_true', help='Compiile it')
    parser.add_argument('-debug', dest='debug', action='store_true', help='debug it')
    return parser.parse_args()

def main():
    args = parse_args()
    code = open(args.file, 'r').read()
    lexer  = Lexer(code)
    if args.debug:
        while 1:
            x = lexer.get_next_token()
            print(x)
            if x.value == TokConsts.EOF:
                break
        # return
    lexer  = Lexer(code)
    parser = Parser(lexer=lexer)
    root = parser.parse()
    if args.debug:
        for child in root.children:
            print(child)
    if args.sim:
        ir = Interpreter(root=root)
        ir.interpret()
    elif args.compile:
        compiler = Compile()
        compiler.compile_ast(root)
        os.system('nasm -f elf64 -o hello.o compile.asm && ld -o hello hello.o && ./hello')
        # os.system('nasm -f macho64 -o hello.o compile.asm && ld -L /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -lSystem -arch x86_64 -macosx_version_min 10.13 -o hello hello.o && ./hello')
    

if __name__ == '__main__':
    main()


