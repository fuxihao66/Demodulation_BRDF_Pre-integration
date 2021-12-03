from multiprocessing import Process
import cv2
import numpy as np
import math
import random
import tqdm
ResolutionPreset = [512, 512]
PI = 3.14159265
spp = 25600
# spp = 2048
threadNum = 16

rowPerThread = ResolutionPreset[0] // threadNum


def ReverseBits32(inputbits):
    bits = ( inputbits << 16) | ( inputbits >> 16)
    bits = ( (bits & 0x00ff00ff) << 8 ) | ( (bits & 0xff00ff00) >> 8 )
    bits = ( (bits & 0x0f0f0f0f) << 4 ) | ( (bits & 0xf0f0f0f0) >> 4 )
    bits = ( (bits & 0x33333333) << 2 ) | ( (bits & 0xcccccccc) >> 2 )
    bits = ( (bits & 0x55555555) << 1 ) | ( (bits & 0xaaaaaaaa) >> 1 )
    return bits

def GenHammersleyTwoDim( sampleIndex, numSamples ):
    RandomX = random.randint(0,0xffff)
    RandomY = random.randint(0,1<<32-1)
    E = ( sampleIndex / numSamples + float( RandomX & 0xffff ) / (1<<16) ) 
    E1 = E - math.floor(E)
    E2 = float( ReverseBits32(sampleIndex) ^ RandomY ) * 2.3283064365386963e-10
    return [E1, E2]


def SampleGGX(randomNum, roughness):

    a = roughness * roughness
    phi = 2 * PI * randomNum[0]
    cosTheta = math.sqrt( (1 - randomNum[1])/(1 + (a * a - 1) * randomNum[1]) )
    sinTheta = math.sqrt( 1 - cosTheta*cosTheta )

    H = np.array([sinTheta*math.cos(phi), sinTheta * math.sin(phi), cosTheta], dtype=np.float32)
    return H
def dot(v1, v2):
    return np.dot(v1, v2)
def saturate(value):
    if value >= 0.:
        if value > 1.:
            return 1.
        else:
            return value
    else:
        return 0.


# def G_smith(roughness, NoV, NoL):
#     a2 = pow(roughness, 4)
#     Vis_SmithV = NoV + math.sqrt( NoV * (NoV - NoV * a2) + a2 )
#     Vis_SmithL = NoL + math.sqrt( NoL * (NoL - NoL * a2) + a2 )
#     return 1/ ( Vis_SmithV * Vis_SmithL )

# def G_schlick(roughness, NoV, NoL):
#     k = roughness * roughness * 0.5
#     Vis_SchlickV = NoV * (1-k) + k
#     Vis_SchlickL = NoL * (1-k) + k
#     return 0.25 / (Vis_SchlickV * Vis_SchlickL)

def rcp(a):
    return 1.0 / a
def Vis_SmithJointApprox(a2, NoV, NoL):
    a = math.sqrt(a2)
    Vis_SmithV = NoL * ( NoV * ( 1 - a ) + a )
    Vis_SmithL = NoV * ( NoL * ( 1 - a ) + a )
    return 0.5 * rcp( Vis_SmithV + Vis_SmithL )

# generate sample x_i ~ p, and return f(x_i)/p(x_i)
def SampleBRDF(NoV, roughness, V, sampleIndex):

    randomNum = GenHammersleyTwoDim(sampleIndex, spp)
    H = SampleGGX(randomNum, roughness)  #Half-Angle Vector
    L = 2 * dot(V, H) * H - V # light angle

    NoL = saturate(L[2])
    NoH = saturate(H[2])
    VoH = dot(V, H)

    if NoL > 0:
        a = roughness * roughness
        a2 = a*a
        Vis = Vis_SmithJointApprox( a2, NoV, NoL )
        NoL_Vis_PDF = NoL * Vis * (4 * VoH / NoH)

        Fc = pow(1 - VoH, 5)
        return np.array([(1 - Fc) * NoL_Vis_PDF, Fc * NoL_Vis_PDF, 0.], dtype=np.float32)
    else:
        return np.array([0., 0., 0.], dtype=np.float32)


def PrecomputePerPixel(nov, roughness):
    result = np.array([0.0, 0.0, 0.0],dtype=np.float32)
    V = np.array([math.sqrt(1 - nov*nov), 0, nov], dtype=np.float32)
    
    for sampleIndex in range(spp):
        value = SampleBRDF(nov, roughness, V, sampleIndex)
        
        result += value
    return result / spp

def Precompute(threadId):
    img = np.zeros([ResolutionPreset[1], ResolutionPreset[0], 3], dtype=np.float32) #  width:nov height:roughness

    for i in tqdm.tqdm(range(rowPerThread * threadId, rowPerThread * threadId + rowPerThread)):
        for j in range(ResolutionPreset[1]):
            nov = (i+0.5) / ResolutionPreset[0]
            roughness = (j+0.5) / ResolutionPreset[1]
            
            img[j][i] = PrecomputePerPixel(nov, roughness)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    cv2.imwrite("Precomputed.{}.exr".format(threadId), img)

           
if __name__ == "__main__":
    precomputeThreadList = list()
        
           
    for threadId in range(threadNum):
        precomputeThreadList.append(Process(target=Precompute, args=(threadId,)))


    for sub_process in precomputeThreadList:
        sub_process.start()
    for sub_process in precomputeThreadList:
        sub_process.join()

    resultImg = np.zeros([ResolutionPreset[1], ResolutionPreset[0], 3], dtype=np.float32) #  width:nov height:roughness

    for threadId in range(threadNum):
        smallImg = cv2.imread("Precomputed.{}.exr".format(threadId), cv2.IMREAD_UNCHANGED)
        resultImg[:,rowPerThread * threadId: rowPerThread * threadId + rowPerThread] = smallImg[:,rowPerThread * threadId: rowPerThread * threadId + rowPerThread]
        cv2.imwrite("Precomputed.exr", resultImg)