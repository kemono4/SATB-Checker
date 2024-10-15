from mido import Message, MidiFile, MidiTrack
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame

mid = MidiFile()
track = MidiTrack()
mid.tracks.append(track)

track.append(Message('program_change',channel=0, program=52,time=0))
track.append(Message('program_change',channel=1, program=52,time=0))
track.append(Message('program_change',channel=2, program=52,time=0))
track.append(Message('program_change',channel=3, program=52,time=0))

pitch={'C':12,'D':14,'E':16,'F':17,'G':19,'A':21,'B':23}

def pitch_to_num(name,num):
    acd=0
    if '#' in name:
        acd=1
        name=name[:-1]
    elif 'b' in name:
        acd=-1
        name=name[:-1]
    acd+=12*num #定義C4=60
    if name in pitch:return pitch[name]+acd

chromatic_scale_sharp=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B']
chromatic_scale_flat=['C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B']

def num_to_pitch(num,acd):
    while num>=12:num-=12
    if acd=='#':return chromatic_scale_sharp[num+1]
    elif acd=='b':return chromatic_scale_flat[num-1]
    else:return chromatic_scale[num]
            
def check_range(ch,chlen,part,mini,maxi):
    first_error=False
    for i in range(chlen):
        if ch[i]>maxi or ch[i]<mini:
            if first_error==False:
                print(f'第{part}聲部第',end='')
                first_error=True
            else:print(',',end='')
            print(i+1,end='')
    return first_error

def consecutive58(interval1,interval2,num,voice1,voice2):
    if interval1==interval2:
        if interval1 in [7,19,31,43,55]:print(f'第{voice1}、{voice2}聲部第{num}、{num+1}音出現平行五度')
        elif interval1 in [0,12,24,36,48]:print(f'第{voice1}、{voice2}聲部第{num}、{num+1}音出現平行八度')
    
def play_midi(file):
    pygame.mixer.init()
    pygame.mixer.music.set_volume(1)
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()

if input('開始檢查(y/n)')=='y':
    ch0name=input('第一聲部，請輸入音名並以/分開：').split('/')
    channel0=[pitch_to_num(x[:-1],int(x[-1:]))for x in ch0name]
    #下略......
    ch1name=input('第二聲部，請輸入音名並以/分開：').split('/')
    channel1=[pitch_to_num(x[:-1],int(x[-1:]))for x in ch1name]
    ch2name=input('第三聲部，請輸入音名並以/分開：').split('/')
    channel2=[pitch_to_num(x[:-1],int(x[-1:]))for x in ch2name]
    ch3name=input('第四聲部，請輸入音名並以/分開：').split('/')
    channel3=[pitch_to_num(x[:-1],int(x[-1:]))for x in ch3name]    

#檢查音域錯誤
    chord_len=len(ch0name)
    
    if check_range(channel0,chord_len,'一',60,81):print('音超過音域')
    if check_range(channel1,chord_len,'二',55,74):print('音超過音域')
    if check_range(channel2,chord_len,'三',48,69):print('音超過音域')
    if check_range(channel3,chord_len,'四',41,62):print('音超過音域')

    major_scale=[2,2,1,2,2,2,1]
    minor_scale=[2,1,2,2,1,2,2]

#檢查數字低音錯誤
    key=input('調性？(C,G#,Ebm,...)：')#nametomidi
    scale=[]
    chromatic_scale=[]
    if key in ['G','D','A','E','B','C#','F#','Em','Bm','F#m','C#m','G#m']:chromatic_scale=chromatic_scale_sharp
    else:chromatic_scale=chromatic_scale_flat#慣用
    
    if 'm' in key:
        Mm='minor'
        #大小調中自然和弦所在級數（degree）不一樣時，會出現大、小、減、屬和半減，若加入教會和其變格和其他非自然調式將會更複雜
        key=key[:-1]
        scale.append(key)#加入主音，即音階第一音
        tonic=pitch_to_num(key,0)
        for g in range(1,7):
            scale.append(num_to_pitch(tonic+sum(minor_scale[:g]),''))
        leading=num_to_pitch(pitch_to_num(scale[-1],0),'#')#導音 
    else:
        Mm='major'
        scale.append(key)
        tonic=pitch_to_num(key,0)
        for g in range(1,7):
            scale.append(num_to_pitch(tonic+sum(major_scale[:g]),''))
        leading=scale[-1]

    if key in ['C#','A#m','F#','D#m']:
        scale=['E#' if n=='F' else n for n in scale]
        scale=['B#' if n=='C' else n for n in scale]
    if key in ['Cb','Abm','Gb','Ebm']:
        scale=['Cb' if n=='B' else n for n in scale]
        scale=['Fb' if n=='E' else n for n in scale]


    scale*=2#防止out of index

    conv_bass=[' ','6','7','65','43','2','42']#慣用數字低音省略記號
    std_bass=['53','63','753','653','643','642','642']

    bass=input('數字低音，請輸入由大至小的數字並以/分開(三和弦原位請用空格，臨時記號在數字前，還原記號請用N)：').split('/')        

    chord=[[]for x in range(chord_len)]#建立二維陣列
    w=0
    for b in bass:#建立和弦構成表
        root=channel3[w]#設置根音
        while root>=12:root-=12
        chord[w]=[ch3name[w][:-1]]#標準化根音成純音名

        if b in conv_bass:b=std_bass[conv_bass.index(b)] 

        if chord[w][0] in scale:root=scale.index(chord[w][0])
        elif chord[w][0][-1]=='#' or chord[w][0][-1]=='b':
            root=scale.index(chord[w][0][:-1])#數字低音不看臨時記號，只看自然音程
        else:
            if chord[w][0]+'#' in chromatic_scale:#還原記號
                root=scale.index(chord[w][0]+'#')    
            else:
                root=scale.index(chord[w][0]+'b') 
                
        b=b[::-1]
        if b[0]in['#','b','N']:
            if len(b)==1:b='3'+b[0]+'5'
            else:b='3'+b

        num=0
        while num <len(b):
            acd=''
            if num<len(b)-1 and b[num+1] =='N':               
                if 'C#' in chromatic_scale:acd='b'
                else:acd='#'
                n=b[num]
                num+=1
            elif num<len(b)-1 and b[num+1] =='#':
                acd='#'
                n=b[num]
                num+=1
            elif num<len(b)-1 and b[num+1] =='b':
                acd='b'
                n=b[num]
                num+=1
            else:n=b[num]
            n=int(n)
            while n>7:n-=7
            temp=scale[root+n-1]#前面scale*=2
            if temp in ['E#','Fb','B#','Cb'] and acd=='':note=temp
            else:note=num_to_pitch(pitch_to_num(temp,0),acd)
                    
            chord[w].append(note)
            num+=1
        w+=1
        
    interval01=[]
    interval12=[]
    interval23=[]
    interval02=[]
    interval03=[]
    interval13=[]

    for i in range(chord_len):

        #確認每一聲部是否出現錯誤音
        if not ch0name[i][:-1] in chord[i]:print(f'第一聲部第{i+1}音出現和弦外錯音')
        if not ch1name[i][:-1] in chord[i]:print(f'第二聲部第{i+1}音出現和弦外錯音')
        if not ch2name[i][:-1] in chord[i]:print(f'第三聲部第{i+1}音出現和弦外錯音')
        if not ch3name[i][:-1] in chord[i]:print(f'第四聲部第{i+1}音出現和弦外錯音')
        #計算音高間距，負數代表聲部交叉違規，大於12/19代表超過完全八/十二度
        interval01.append(channel0[i]-channel1[i])
        interval12.append(channel1[i]-channel2[i])
        interval23.append(channel2[i]-channel3[i])
        #用於判斷平行58
        interval02.append(channel0[i]-channel2[i])
        interval03.append(channel0[i]-channel3[i])
        interval13.append(channel1[i]-channel3[i])
        #檢查間距違規
        if interval01[i]<0:print(f'第一與第二聲部第{i+1}音出現聲部交叉')
        elif interval01[i]>12:print(f'第一與第二聲部第{i+1}音超過完全八度')
        if interval12[i]<0:print(f'第二與第三聲部第{i+1}音出現聲部交叉')
        elif interval12[i]>12:print(f'第二與第三聲部第{i+1}音超過完全八度')
        if interval23[i]<0:print(f'第三與第四聲部第{i+1}音出現聲部交叉')
        elif interval23[i]>19:print(f'第三與第四聲部第{i+1}音超過完全十二度')
        if interval02[i]<0:print(f'第一與第三聲部第{i+1}音出現聲部交叉')
        if interval03[i]<0:print(f'第一與第四聲部第{i+1}音出現聲部交叉')
        if interval13[i]<0:print(f'第二與第四聲部第{i+1}音出現聲部交叉')
        #檢查聲部交越，當前音不能超過前一個和弦其上下兩聲部的音
        #1比前2低嗎 21 23 32 34 43
        if i>0:
            if channel0[i]<channel1[i-1]:
                print(f'第一聲部第{i+1}音出現聲部交越')
            if channel1[i]>channel0[i-1] or channel1[i]<channel2[i-1]:
                print(f'第二聲部第{i+1}音出現聲部交越')
            if channel2[i]>channel1[i-1] or channel2[i]<channel3[i-1]:
                print(f'第三聲部第{i+1}音出現聲部交越')
            if channel3[i]>channel2[i-1]:
                print(f'第四聲部第{i+1}音出現聲部交越')
    

    Aug_4th=[6,18,30,42,54]#三全音
    
    for i in range(chord_len):
        #檢查重複音禁忌
        #用channel0123彼此相減來計算有無三全音   #dim重複三，避免三全音
        l=0
        if channel0[i]-channel1[i] in Aug_4th:l+=1
        if channel0[i]-channel2[i] in Aug_4th:l+=1
        if channel0[i]-channel3[i] in Aug_4th:l+=1
        if channel1[i]-channel2[i] in Aug_4th:l+=1
        if channel1[i]-channel3[i] in Aug_4th:l+=1
        if channel2[i]-channel3[i] in Aug_4th:l+=1
        if l>1:print(f'第{i+1}個和弦出現三全音重複')

        #任何情況下，導音(大調、和聲小調中第7音)都不可能重複
        l=0
        if ch0name[i][:-1]==leading:l+=1
        if ch1name[i][:-1]==leading:l+=1
        if ch2name[i][:-1]==leading:l+=1
        if ch3name[i][:-1]==leading:l+=1
        if l>1:print(f'第{i+1}個和弦出現導音重複')
    
        #七和弦的七度音 
        if ('7' in bass[i]) or ('6' in bass[i] and '5' in bass[i]) or ('3' in bass[i] and '4' in bass[i]) or ('2' in bass[i]):
            l=0
            if ch0name[i][:-1]==chord[i][-1]:l+=1
            if ch1name[i][:-1]==chord[i][-1]:l+=1
            if ch2name[i][:-1]==chord[i][-1]:l+=1
            if ch3name[i][:-1]==chord[i][-1]:l+=1
            if l>1:print(f'第{i+1}個和弦出現七度音重複')
    
        #三和弦二轉優先重複5
        if bass[i]=='64':
            l=0
            if ch0name[i][:-1]==ch3name[i][:-1]:l+=1
            if ch1name[i][:-1]==ch3name[i][:-1]:l+=1
            if ch2name[i][:-1]==ch3name[i][:-1]:l+=1
            if l==0:print(f'第{i+1}個和弦應優先重複五度(三和弦第二轉位)')

    minus0=[]
    minus1=[]
    minus2=[]
    minus3=[]
     
    for i in range(chord_len-1):#最後一個不用向後確認
        #判斷四部同向（channel後減前全大於或小於0
        minus0.append(channel0[i+1]-channel0[i])
        minus1.append(channel1[i+1]-channel1[i])
        minus2.append(channel2[i+1]-channel2[i])
        minus3.append(channel3[i+1]-channel3[i])
        if minus0[i]>0 and minus1[i]>0 and minus2[i]>0 and minus3[i]>0:
            print(f'第{i+1},{i+2}個和弦間出現四部同向')
        elif minus0[i]<0 and minus1[i]<0 and minus2[i]<0 and minus3[i]<0:
            print(f'第{i+1},{i+2}個和弦間出現四部同向')

        #平行58（找下一小節
        if channel0[i]!=channel0[i+1]:
            consecutive58(interval01[i],interval01[i+1],i+1,'一','二')
        if channel1[i]!=channel1[i+1]:
            consecutive58(interval12[i],interval12[i+1],i+1,'二','三')
        if channel2[i]!=channel2[i+1]:
            consecutive58(interval23[i],interval23[i+1],i+1,'三','四')
        if channel0[i]!=channel0[i+1]:
            consecutive58(interval02[i],interval02[i+1],i+1,'一','三')
        if channel0[i]!=channel0[i+1]:
            consecutive58(interval03[i],interval03[i+1],i+1,'一','四')
        if channel1[i]!=channel1[i+1]:
            consecutive58(interval13[i],interval13[i+1],i+1,'二','四')
        
        #隱伏58（if進入58:找上一小節是否第一部跳進，一四同向）
        if (minus0[i]>2 and minus3[i]>0) or (minus0[i]<-2 and minus3[i]<0):#增二度級進也是禁忌，故直接當小三度處理即可
            if not interval03[i] in [0,12,24,36,48] and interval03[i+1] in [0,12,24,36,48]:
                print(f'第{i+2}個和弦出現隱伏八度')
            if not interval03[i] in [7,19,31,43,55] and interval03[i+1] in [7,19,31,43,55]:
                print(f'第{i+2}個和弦出現隱伏五度')


    print('判斷結束')
    
    if input('是否輸出midi和播放(y/n)')=='y':
        filname=input('輸入檔名：')
        length=[float(x) for x in input('輸入節奏並以/分開(1表示四分音符,2表示兩倍長度即二分音符)：').split('/')]
        if len(length)==1:length*=chord_len
        bpm=120
        quarter=60/bpm*1000
        for i in range(chord_len):
            #track.append音量在0-127、以及time為整數round()四捨五入
            track.append(Message('note_on',note=channel0[i],time=0,channel=0))
            track.append(Message('note_on',note=channel1[i],time=0,channel=1))
            track.append(Message('note_on',note=channel2[i],time=0,channel=2))
            track.append(Message('note_on',note=channel3[i],time=0,channel=3))

            track.append(Message('note_off',note=channel0[i],time=round(length[i]*quarter),channel=0))
            track.append(Message('note_off',note=channel1[i],time=0,channel=1))
            track.append(Message('note_off',note=channel2[i],time=0,channel=2))
            track.append(Message('note_off',note=channel3[i],time=0,channel=3))
    
        mid.save(f'{filname}.mid')
        play_midi(f'{filname}.mid')
