/***************************************************************************
 # Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
 #
 # Redistribution and use in source and binary forms, with or without
 # modification, are permitted provided that the following conditions
 # are met:
 #  * Redistributions of source code must retain the above copyright
 #    notice, this list of conditions and the following disclaimer.
 #  * Redistributions in binary form must reproduce the above copyright
 #    notice, this list of conditions and the following disclaimer in the
 #    documentation and/or other materials provided with the distribution.
 #  * Neither the name of NVIDIA CORPORATION nor the names of its
 #    contributors may be used to endorse or promote products derived
 #    from this software without specific prior written permission.
 #
 # THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS "AS IS" AND ANY
 # EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 # IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 # PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 # CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 # EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 # PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 # PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
 # OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 # (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 # OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 **************************************************************************/
#include "DemodulatePass.h"

// Don't remove this. it's required for hot-reload to function properly
extern "C" __declspec(dllexport) const char* getProjDir()
{
    return PROJECT_DIR;
}

extern "C" __declspec(dllexport) void getPasses(Falcor::RenderPassLibrary& lib)
{
    lib.registerClass("DemodulatePass", "Render Pass Template", DemodulatePass::create);
}


namespace
{
    const char kDesc[] = "DemodulatePass";
    const char kOutput[] = "OutAlbedo";
    const char kInputAlbedo[] = "InputAlbedo";
    const char kInputRoughness[] = "InputRoughness";
    const char kInputNov[] = "InputNov";
    const char kInputPrecomputed[] = "InputPrecomputed";
    const char kInputSpecular[] = "InputSpecular";
    const char kInputMetallic[] = "InputMetallic";

    const char kComputeProgram[] = "RenderPasses/DemodulatePass/DoDemodulation.cs.slang";
}

DemodulatePass::DemodulatePass()
{
    
    Sampler::Desc samplerDesc;
    samplerDesc.setFilterMode(Sampler::Filter::Linear, Sampler::Filter::Linear, Sampler::Filter::Linear);
    samplerDesc.setAddressingMode(Sampler::AddressMode::Clamp, Sampler::AddressMode::Clamp, Sampler::AddressMode::Clamp);
    samplerDesc.setBorderColor(Falcor::float4(0, 0, 0, 0));
    mpLinearSampler = Sampler::create(samplerDesc);

    mpProgramCS = ComputeProgram::createFromFile(kComputeProgram, "Main");
    mpVarsCS = ComputeVars::create(mpProgramCS->getReflector());
    mpStateCS = ComputeState::create();
}

DemodulatePass::SharedPtr DemodulatePass::create(RenderContext* pRenderContext, const Dictionary& dict)
{
    SharedPtr pPass = SharedPtr(new DemodulatePass);
    return pPass;
}

Dictionary DemodulatePass::getScriptingDictionary()
{
    return Dictionary();
}

RenderPassReflection DemodulatePass::reflect(const CompileData& compileData)
{
    // Define the required resources here
    RenderPassReflection reflector;
    reflector.addInput(kInputAlbedo, "input albedo");
    reflector.addInput(kInputRoughness, "input roughness");
    reflector.addInput(kInputNov, "input nov");
    reflector.addInput(kInputPrecomputed, "input precomputed");
    reflector.addInput(kInputSpecular, "input specular");
    reflector.addInput(kInputMetallic, "input metallic");

    reflector.addOutput(kOutput,"output color").format(ResourceFormat::RGBA32Float);
    return reflector;
}

void DemodulatePass::execute(RenderContext* pRenderContext, const RenderData& renderData)
{

    uint width = renderData[kInputAlbedo]->asTexture()->getWidth();
    uint height = renderData[kInputAlbedo]->asTexture()->getHeight();

    mpVarsCS["gAlbedo"] = renderData[kInputAlbedo]->asTexture();
    mpVarsCS["gRoughness"] = renderData[kInputRoughness]->asTexture();
    mpVarsCS["gNov"] = renderData[kInputNov]->asTexture();
    mpVarsCS["gPrecomputed"] = renderData[kInputPrecomputed]->asTexture();
    mpVarsCS["gSpecular"] = renderData[kInputSpecular]->asTexture();
    mpVarsCS["gMetallic"] = renderData[kInputMetallic]->asTexture();

    mpVarsCS["gOutputAlbedo"] = renderData[kOutput]->asTexture();

    mpVarsCS["gSampler_linear"] = mpLinearSampler;


    uint3 numGroups = div_round_up(uint3(width, height, 1u), mpProgramCS->getReflector()->getThreadGroupSize());
    mpStateCS->setProgram(mpProgramCS);
    pRenderContext->dispatch(mpStateCS.get(), mpVarsCS.get(), numGroups);
}

void DemodulatePass::renderUI(Gui::Widgets& widget)
{
}
