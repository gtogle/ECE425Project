#global elements such as the register file and memory addresses set as arrays, as well as the program counter set to 0
regFile= [0]*32
memSpace = [0]*2048
programCounter = 0

# this is the 1 bit ALU that will be used as to help create the 32 bit ALU later, contains add, subtract, and and 
def ALU(bit1 , bit2, operation, carry1):
    if (operation == "sub"):
        bit2 = bit2^ 1
    if (operation == "add") or (operation == "sub"):
        carry2 = (bit1 & bit2) | (carry1 & (bit1 ^ bit2))
        result = bit1 ^ bit2 ^carry1
    
        return result, carry2
    elif operation == "and":
        carry2 = 0
        result = bit1 & bit2
        return result, carry2
    


#32 bit version using the 1 bit ALU from earlier, letting them be used in the upcoming functions
def ALU32bit(num1, num2, operation):
    num1Array = []
    num2Array = []
    finalArray =[0]*32
    for i in range(32):
        currentNum1Bit = (num1 >> i)& 1
        currentNum2Bit = (num2 >> i)& 1
        num1Array.append(currentNum1Bit)
        num2Array.append(currentNum2Bit)  
    if operation == "add" or operation == "sub":
        if operation == "sub":
            currentCarry2 = 1
        else:
            currentCarry2 = 0
        currentFinalBit = 0
        if operation == "add":
            for i in range(32):
                currentFinalBit, currentCarry2 = ALU(num1Array[i], num2Array[i], "add", currentCarry2)
                finalArray[i]= currentFinalBit
        else:
            for i in range(32):
                currentFinalBit, currentCarry2 = ALU(num1Array[i], num2Array[i], "sub", currentCarry2)
                finalArray[i]= currentFinalBit
        finalNum = 0
        for i in range(32):
            finalNum |=(finalArray[i] << i)
        return finalNum
        
    if operation == "and":
        currentCarry2 = 0
        for i in range(32):
            currentFinalBit, currentCarry2 = ALU(num1Array[i], num2Array[i], "and", currentCarry2)
            finalArray[i]= currentFinalBit
        finalNum = 0
        for i in range(32):
            finalNum |= (finalArray[i] << i)
        return finalNum
# function that allows 16 bit integers to be unsigned extended, which means adding 0's to make it 32 bit
def unsignedExtend(num):
    return num & 0x0000FFFF

#function that allows 16 bit integers to be signed extended, which depended on the value of the sign bit
def signExtend(num):
    if (num & 0x8000) == 0x8000:
        return num | 0xFFFF0000
    else:
        return num & 0x0000FFFF


#function that allows the ability to load a value from a memory address into a register      
def loadWord(destReg, offset, memoryRegister):
    global programCounter
    programCounter = ALU32bit(programCounter, 0x00000001, "add")
    preShiftMemAddress = regFile[memoryRegister]
    trueOffset = signExtend(offset)
    trueMemAddress = ALU32bit(trueOffset, preShiftMemAddress, "add")
    regFile[destReg] = memSpace[trueMemAddress]
    return trueMemAddress, regFile[destReg]

#function that allows the ability to store a value into a memory address from a register
def storeWord(currentRegister, offset, memRegister):
    global programCounter
    programCounter = ALU32bit(programCounter, 0x00000001, "add")
    preShiftMemAddress = regFile[memRegister]
    trueOffset = signExtend(offset)
    trueMemAddress = ALU32bit(trueOffset, preShiftMemAddress, "add")
    memSpace[trueMemAddress] = regFile[currentRegister]
    return trueMemAddress, memSpace[trueMemAddress]

#function that allows addition
def add(sumRegister, addRegister1, addRegister2):
    global programCounter
    programCounter = ALU32bit(programCounter, 0x00000001, "add")
    regFile[sumRegister] = ALU32bit(regFile[addRegister1], regFile[addRegister2], "add")
    return regFile[sumRegister]

#function that allows branching to a specific program counter offset if not equal
def branchNotEqual(register1, register2, offset):
    trueOffset = signExtend(offset)
    global programCounter
    programCounterAdd1 = ALU32bit(programCounter, 0x00000001 , "add")
    compareReg = ALU32bit(regFile[register1], regFile[register2], "sub")
    if compareReg == 0:
        programCounter = programCounterAdd1
    else:
        programCounter = ALU32bit(programCounterAdd1, trueOffset, "add")
    return programCounter

#function that allows the branching to a specific program counter offset if equal
def branchIfEqual(register1, register2, offset):
    trueOffset = signExtend(offset)
    global programCounter
    programCounterAdd1 = ALU32bit(programCounter, 0x00000001 , "add")
    compareReg = ALU32bit(regFile[register1], regFile[register2], "sub")
    if compareReg != 0 :
        programCounter = programCounterAdd1
    else:
        programCounter = ALU32bit(programCounterAdd1, trueOffset, "add")
    return programCounter

#function that allows the bitwise and of a register and an immediate
def andImmediate(register1, register2, immediate):
    global programCounter
    programCounter = ALU32bit(programCounter, 0x00000001, "add")
    trueImmediate =unsignedExtend(immediate)
    regFile[register1]= ALU32bit(regFile[register2], trueImmediate, "and")
    return regFile[register1]

# test files to test all six instructions
t3 = 11
offsetLW = 300
s2 = 18
regFile[s2]=50
memSpace[350] = 15
memAddLW, valueInt3 = loadWord(t3, offsetLW, s2)
print("LOADWORD TEST")
print(f"Memory address after offset in loadWord: {memAddLW}")
print(f"Value in register $t3: {valueInt3}")

print()
print("STOREWORD TEST")
t6 = 14
offsetSW = 400
s7 = 23
regFile[s7]= 90
regFile[t6] = 25
memAddSW, valueinMemAdd = storeWord(t6, offsetSW, s7)
print(f"Memory address after offset in storeWord 400 + 90: {memAddSW}")
print(f"Value in memory address after offset $t3: {valueinMemAdd}")
print()

print("ADD TEST")
t5 = 13
t3 = 11
s1 = 17
regFile[t3] = 8
regFile[s1] = 4
valueInt5 = add(t5, t3, s1)
print(f"Value in register $t5 after addition (8+ 4 =12):{valueInt5}")

print()
print("BNE TEST")
programCounter = 0
s6 = 22
t5 = 13
offsetBNE = 200
regFile[s6]= 9
regFile[t5] = 8
pcforBNE = branchNotEqual(s6, t5, offsetBNE)
print(f"Program counter after branch not equal(9 and 8 dont equal each other):{pcforBNE}")

print("BNE TEST part 2")
programCounter = 0
s6 = 22
t5 = 13
offsetBNE = 200
regFile[s6]= 9
regFile[t5] = 9
pcforBNE = branchNotEqual(s6, t5, offsetBNE)
print(f"Program counter after branch not equal(9 and 9 do equal each other):{pcforBNE}")

print("BEQ TEST")
programCounter = 0
s3 = 19
t2 = 10
offsetBEQ = 20
regFile[s3] = 14
regFile[t2] = 14
pcforBEQ = branchIfEqual(s3, t2, offsetBEQ)
print(f"Program counter after branch if equal(14 and 14 do equal each other):{pcforBEQ}")

print("BEQ TEST part 2")
programCounter = 0
s3 = 19
t2 = 10
offsetBEQ = 20
regFile[s3] = 15
regFile[t2] = 14
pcforBEQ2 = branchIfEqual(s3, t2, offsetBEQ)
print(f"Program counter after branch if equal(15 and 14 dont equal each other):{pcforBEQ2}")

print()
print("ANDI TEST")
t1 = 9
s4 = 20

immediateANDI = 0x1101
regFile[s4] = 0x11110101
valueint1 = andImmediate(t1, s4, immediateANDI)
print(f"Value in register $t1 after ANDI: 0x{valueint1:08X}")















