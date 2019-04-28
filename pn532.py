import RPi.GPIO as gpio
import serial
import time
import wiringpi
import struct
di=13
gpio.setmode(gpio.BCM)
gpio.setup(di,gpio.OUT)
gpio.setwarnings(False)
ser=serial.Serial("/dev/ttyAMA0",115200)
key=b'\xff\xff\xff\xff\xff\xff'
key1=b'\x00\x00\x00\x00\x00\x00'
uid=b''
#wd=[55,55,00,00,88,94,ff,ef,9b]
def wakeup():
    cmdstr=b'\x55\x55\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\x03\xfd\xd4\x14\x01\x17\x00'
    ser.write(cmdstr)
    anstr=ser.read(15)
    if anstr==b'\x00\x00\xff\x00\xff\x00\x00\x00\xff\x02\xfe\xd5\x15\x16\x00':
        return True
    else:
        return False
def getuid():
    cmdstr=b'\x00\x00\xff\x04\xfc\xd4\x4a\x01\x00\xe1\x00'
    ser.write(cmdstr)
    print("Please put a card on pn532:")
    anstr=ser.read(25)#Here will stop until put a card to pn532  
    uid=struct.pack("!4s",anstr[19:23])
    return uid
def readblock(block):
    cmdstr=b'\x00\x00\xff\x05\xfb\xd4\x40\x01\x30'+block
    dcs=getdcs(cmdstr[5:20])
    
    cmdstr=cmdstr+dcs+b'\x00'
    #print("read_command:"+str(cmdstr))
    ser.write(cmdstr)
    #print("reading......")
    time.sleep(0.1)
    n=ser.inWaiting()
    anstr=ser.read(n)
    status=anstr[12:14]
    #print(anstr)
    if status==b'\x41\x00':
        blockdata=anstr[14:30]
        return blockdata
    else:
        return False
def writeblock(block,data):
    cmdstr=b'\x00\x00\xff\x15\xeb\xd4\x40\x01\xa0'+block+data
    dcs=getdcs(cmdstr[5:26])
    
    cmdstr=cmdstr+dcs+b'\x00'
    #print("write_command:"+str(cmdstr))
    ser.write(cmdstr)
    #print("writing......")
    time.sleep(1)
    n=ser.inWaiting()
    anstr=ser.read(n)
    status=anstr[12:14]
    print(anstr)
    if status==b'\x41\x00':
        return True
    else:
        return False
def getdcs(data):
    he=data
    zonghe=0
    for shu in he:
        zonghe=zonghe+shu
    zonghebytes=struct.pack("!H",zonghe)
    cha=256-zonghebytes[1]
    ack=struct.pack("!H",cha)
    ack=struct.pack("B",ack[1])
    return ack
def confirmkey(section,key,uid):
    cmdstr=b'\x00\x00\xff\x0f\xf1\xd4\x40\x01\x60'+section+key+uid
    #get dcs
    dcs=getdcs(cmdstr[5:20])
    cmdstr=cmdstr+dcs+b'\x00'
    #print("confirm_command:"+str(cmdstr))
    ser.write(cmdstr)
    #print("key confirming......")
    time.sleep(0.1)
    n=ser.inWaiting()
    anstr=ser.read(n)
    gpio.output(di,True)
    time.sleep(0.2)
    gpio.output(di,False)
    status=anstr[12:14]
    #print(anstr)
    if status==b'\x41\x00':
        return True
    else:
        return False
def findpassword():
    for x1 in range(255,-1,-1):
        p1=struct.pack("B",x1)
        for x2 in range(255,-1,-1):
            p2=struct.pack("B",x2)
            for x3 in range(255,-1,-1):
                p3=struct.pack("B",x3)
                for x4 in range(255,-1,-1):
                    p4=struct.pack("B",x4)
                    for x5 in range(255,-1,-1):
                        p5=struct.pack("B",x5)
                        for x6 in range(255,-1,-1):
                            p6=struct.pack("B",x6)
                            key=p1+p2+p3+p4+p5+p6
                            cmdstr=b'\x00\x00\xff\x0f\xf1\xd4\x40\x01\x60\x08'+key+uid
                            he=cmdstr[5:20]
                            zonghe=0
                            for shu in he:
                                zonghe=zonghe+shu
                            zonghebytes=struct.pack("!H",zonghe)
                            cha=256-zonghebytes[1]
                            ack=struct.pack("!H",cha)
                            ack=struct.pack("B",ack[1])
                            cmdstr=cmdstr+ack+b'\x00'
                            print(cmdstr)
                            ser.write(cmdstr)
                            anstr=ser.read(16)
                            isok=anstr[12:14]
                            if isok[1]==0:
                                print(key)
                                exit()
if __name__=='__main__':
    try:
        x=1
        while x==1:
            if wakeup():
                print("weakup successful!")
                uid=getuid()
                print(uid)
                block=b'\x01'
                if confirmkey(block,key,uid):
                    print("Password correct!")
                    readvalue=readblock(block)
                    if not readvalue:
                        print("read error!")
                    else:
                        print(readvalue)
                    wdata=b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f'
                    if writeblock(block,wdata):
                        print("write ok")
                    else: 
                        print("write fail")
                    readvalue=readblock(block)
                    if not readvalue:
                        print("read error!")
                    else:
                        print(readvalue)
                else:
                    print("Password incorrect!")
                #findpassword()
                #confirmkey(b'\x08')
            else:
                print("weakup failed!")
            x=2
    except Exception as e:
        gpio.output(di,True)
        gpio.cleanup()
        print(e)
        if ser!=None:
            ser.close()
            
            
