import re


def read_instructions() -> tuple:
    types = dict()
    opcodes = dict()
    functions = dict()

    for line in open("instructions.txt", 'r').readlines():
        line = line[:-1].split(';')
        types[line[0]] = line[1]
        opcodes[line[0]] = line[2]
        if line[1] == 'r':
            functions[line[0]] = line[3]

    return types, opcodes, functions


def read_registers() -> dict:
    registers = dict()

    for line in open("registers.txt", 'r').readlines():
        line = line[:-1].split(';')
        registers[line[0]] = line[1]

    return registers


def dec_to_bin(dec_value: str, size: int) -> str:
    dec_value_int = int(dec_value)

    if dec_value_int < 0:
        raise ValueError("Valor imediato negativo.")
    elif dec_value_int >= 2 ** size:
        raise ValueError("Valor imediato maior do que o tamanho suportado.")
    else:
        bin_value = bin(dec_value_int)[2:]
        return "0" * (size - len(bin_value)) + bin_value


class Instruction:
    type_dict, opcode_dict, function_dict = read_instructions()
    register_dict = read_registers()

    def __init__(self, name: str, instruction_list: list, has_label_start: bool, has_label_final: bool):
        self.name = name
        self.opcode = Instruction.opcode_dict[name]
        self.type = Instruction.type_dict[name]
        self.has_immediate = False
        self.has_label_inicio = has_label_start
        self.has_label_final = has_label_final
        # tratando os registradores sem tratar o caso do label
        if self.type != "j":
            if self.name == "jr":
                self.rs = Instruction.register_dict[instruction_list[1]]
            elif self.type == "r" and not has_label_start:
                if name != "sll" and name != "srl":
                    self.rd = Instruction.register_dict[instruction_list[1]]
                    self.rs = Instruction.register_dict[instruction_list[2]]
                    self.rt = Instruction.register_dict[instruction_list[3]]
                else:
                    self.rs = dec_to_bin('0', 5)
                    self.rt = Instruction.register_dict[instruction_list[1]]
                    self.rd = Instruction.register_dict[instruction_list[2]]
            elif self.type == "i" and not has_label_start:
                if name == 'lw' or name == 'sw':
                    rs = instruction_list[-1]
                    rs = rs.split("(")[1].replace(")", '')
                    self.rs = Instruction.register_dict[rs]
                else:
                    self.rs = Instruction.register_dict[instruction_list[2]]
                self.rt = Instruction.register_dict[instruction_list[1]]

        # function and shamt sem tratar o label no final
        if self.type == "r":
            self.function = Instruction.function_dict[name]
            if name == 'sll' or name == "srl":
                self.has_immediate = True
                self.shamt = dec_to_bin(instruction_list[-1], 5)
            else:
                self.shamt = dec_to_bin('0', 5)
        if (self.type == "i" or self.type == "j") and not self.has_label_final:
            immediate = instruction_list[-1]
            if name == "lw" or name == "sw":
                immediate = immediate.split("(")[0]
                self.immediate = dec_to_bin(immediate, 16)
            self.immediate = dec_to_bin(immediate, 16)


def read_asm() -> list:
    pattern = r"[ ,]"
    lista_de_instrucao = list()
    for line in open("exemplo.asm", "r").readlines():
        line = re.split(pattern, line.replace("\n", "").lower())
        for i in range(line.count("")):
            line.remove("")
        lista_de_instrucao.append(line)
    return lista_de_instrucao


def check_instruction(list_instruction: list):
    last_word_instruction = list_instruction[-1]
    has_label_init = False
    has_label_final = False

    if ":" in list_instruction[0]:
        has_label_init = True
    if last_word_instruction.isalpha():
        has_label_final = True

    if not has_label_init:
        instruction_obj = Instruction(list_instruction[0], list_instruction, has_label_init, has_label_final)
    else:
        instruction_obj = Instruction(list_instruction[1], list_instruction, has_label_init, has_label_final)

    if instruction_obj.type == 'i':
        instruction_obj.has_immediate = True

    return instruction_obj


def transforming_instruction(list_instruction):
    for l in list_instruction:
        instruction_obj = check_instruction(l)

        print(f'Nome = {instruction_obj.name}')
        print(f'Opcode = {instruction_obj.opcode}')
        print(f'Tipo = {instruction_obj.type}')
        if instruction_obj.type == "r":
            print(f'Shamt = {instruction_obj.shamt}')
            print(f'Function {instruction_obj.function}')
        if (instruction_obj.type == "i" or instruction_obj.type == "j") and not instruction_obj.has_label_final:
            print(f'Endereço/imediato = {instruction_obj.immediate}')

        if instruction_obj.type != "j" and not instruction_obj.has_label_inicio:
            print(f'RS = {instruction_obj.rs}')
            if instruction_obj.name != 'jr':
                print(f'RT {instruction_obj.rt}')
                if instruction_obj.type == "r":
                    print(f'RD {instruction_obj.rd}')
        print()


transforming_instruction(read_asm())
