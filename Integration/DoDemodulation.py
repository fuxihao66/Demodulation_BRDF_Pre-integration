from falcor import *
import os 
from math import ceil,floor
from math import exp
from math import pow

basePath = "E:/TestSet/bunkerTest/BK_Test_0/"
prefix = "Bunker"
def render_graph_DefaultRenderGraph():
    g = RenderGraph('DefaultRenderGraph')
    loadRenderPassLibrary('BSDFViewer.dll')
    loadRenderPassLibrary('AccumulatePass.dll')
    loadRenderPassLibrary('Antialiasing.dll')
    loadRenderPassLibrary('DepthPass.dll')
    loadRenderPassLibrary('SkyBox.dll')
    loadRenderPassLibrary('DebugPasses.dll')
    loadRenderPassLibrary('BlitPass.dll')
    loadRenderPassLibrary('CSM.dll')
    loadRenderPassLibrary('ErrorMeasurePass.dll')
    loadRenderPassLibrary('ForwardLightingPass.dll')
    loadRenderPassLibrary('GBuffer.dll')
    loadRenderPassLibrary('ImageLoader.dll')
    loadRenderPassLibrary('MegakernelPathTracer.dll')
    loadRenderPassLibrary('MinimalPathTracer.dll')
    loadRenderPassLibrary('PassLibraryTemplate.dll')
    loadRenderPassLibrary('WhittedRayTracer.dll')
    loadRenderPassLibrary('PixelInspectorPass.dll')
    loadRenderPassLibrary('SSAO.dll')
    loadRenderPassLibrary('SVGFPass.dll')
    loadRenderPassLibrary('TemporalDelayPass.dll')
    loadRenderPassLibrary('ToneMapper.dll')
    loadRenderPassLibrary('Utils.dll')
    loadRenderPassLibrary('DemodulatePass.dll')
    DemodulatePass = createPass('DemodulatePass', {})
    g.addPass(DemodulatePass, 'DemodulatePass')
    
    ImageLoader = createPass('ImageLoader', {'filename': basePath+prefix+"BaseColor.0058.exr", 'mips': False, 'srgb': False, 'arrayIndex': 0, 'mipLevel': 0})
    g.addPass(ImageLoader, 'ImageLoader_input_1')


    ImageLoader_ = createPass('ImageLoader', {'filename': basePath+prefix+"Roughness.0058.exr", 'mips': False, 'srgb': False, 'arrayIndex': 0, 'mipLevel': 0})
    g.addPass(ImageLoader_, 'ImageLoader_input_2')

    ImageLoader__ = createPass('ImageLoader', {'filename': basePath+prefix+"NoV.0058.exr", 'mips': False, 'srgb': False, 'arrayIndex': 0, 'mipLevel': 0})
    g.addPass(ImageLoader__, 'ImageLoader_input_3')


    ImageLoader___ = createPass('ImageLoader', {'filename': "D:/Falcor-master/Source/RenderPasses/DemodulatePass/Precomputed.exr", 'mips': False, 'srgb': False, 'arrayIndex': 0, 'mipLevel': 0})
    g.addPass(ImageLoader___, 'ImageLoader_input_4')

    ImageLoader____ = createPass('ImageLoader', {'filename': basePath+prefix+"Specular.0058.exr", 'mips': False, 'srgb': False, 'arrayIndex': 0, 'mipLevel': 0})
    g.addPass(ImageLoader____, 'ImageLoader_input_5')

    ImageLoader_____ = createPass('ImageLoader', {'filename': basePath+prefix+"Metallic.0058.exr", 'mips': False, 'srgb': False, 'arrayIndex': 0, 'mipLevel': 0})
    g.addPass(ImageLoader_____, 'ImageLoader_input_6')


    g.addEdge('ImageLoader_input_1.dst', 'DemodulatePass.InputAlbedo')
    g.addEdge('ImageLoader_input_2.dst', 'DemodulatePass.InputRoughness')
    g.addEdge('ImageLoader_input_3.dst', 'DemodulatePass.InputNov')
    g.addEdge('ImageLoader_input_4.dst', 'DemodulatePass.InputPrecomputed')
    g.addEdge('ImageLoader_input_5.dst', 'DemodulatePass.InputSpecular')
    g.addEdge('ImageLoader_input_6.dst', 'DemodulatePass.InputMetallic')
    g.markOutput('DemodulatePass.OutAlbedo')
    return g

    
resizeSwapChain(1280, 720)

DefaultRenderGraph = render_graph_DefaultRenderGraph()
try: m.addGraph(DefaultRenderGraph)
except NameError: None


fc.outputDir = "D:/Falcor-master/"
fc.baseFilename = f"res"
renderFrame()
fc.capture()
