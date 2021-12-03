
Texture2D gAlbedo;
Texture2D gRoughness;
Texture2D gNov;
Texture2D gPrecomputed;
Texture2D gSpecular;
Texture2D gMetallic;
SamplerState gSampler_linear;

RWTexture2D<float4> gOutputAlbedo;


// TODO: 确定UE的brdf   尤其是albedo是不是和这些是相加关系
[numthreads(1, 1, 1)]
void Main(uint3 id : SV_DispatchThreadID){
    float2 uv = float2(gNov[id.xy].x, gRoughness[id.xy].x);
    float2 preComputedValue = gPrecomputed.SampleLevel(gSampler_linear, uv, 0.0).xy;
    float3 albedo = gAlbedo[id.xy].xyz;

    float3 specular = gSpecular[id.xy].xxx;
    float3 metallic = gMetallic[id.xy].xxx;

    float3 specularColor = lerp(0.08 * specular, albedo, metallic);

    float4 returnValue = float4(0.0, 0.0, 0.0, 1.0);
    returnValue.xyz = albedo + preComputedValue.x * specularColor + preComputedValue.yyy;
    gOutputAlbedo[id.xy] = returnValue;
}
