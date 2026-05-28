from __future__ import annotations

import base64
import time
from io import BytesIO
from typing import Any

from openai import OpenAI
from PIL import Image

from .config import Settings
from .mermaid import graph_to_mermaid, normalize_graph
from .models import GenerateResponse, GraphEdge, GraphNode, MethodGraph


SYSTEM_PROMPT = """你是科研方法图整理助手。请把用户的口头描述和草图合并成清晰的论文风格方法流程图。
要求：
1. 优先保留输入、关键模块、融合/推理步骤、输出、评测指标之间的方向关系。
2. 节点标签短而具体，适合放在方法图中。
3. 不确定的草图内容写入 warnings，不要编造过细模块。
4. 输出必须满足给定 JSON schema。"""


class SketchVoiceGenerator:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or Settings()
        self.client = (
            OpenAI(api_key=self.settings.openai_api_key, base_url=self.settings.openai_base_url)
            if self.settings.openai_api_key
            else None
        )

    async def generate(
        self,
        *,
        sketch_bytes: bytes | None,
        sketch_content_type: str | None,
        audio_bytes: bytes | None,
        audio_filename: str | None,
        audio_content_type: str | None,
        transcript: str | None,
        direction: str,
    ) -> GenerateResponse:
        timings: dict[str, int] = {}
        start = time.perf_counter()
        final_transcript = await self._resolve_transcript(
            audio_bytes=audio_bytes,
            audio_filename=audio_filename,
            audio_content_type=audio_content_type,
            transcript=transcript,
        )
        timings["asr"] = int((time.perf_counter() - start) * 1000)

        graph_start = time.perf_counter()
        graph = await self._build_graph(
            sketch_bytes=sketch_bytes,
            sketch_content_type=sketch_content_type,
            transcript=final_transcript,
        )
        graph = normalize_graph(graph)
        timings["graph"] = int((time.perf_counter() - graph_start) * 1000)

        mermaid_start = time.perf_counter()
        mermaid = graph_to_mermaid(graph, direction=direction)
        timings["mermaid"] = int((time.perf_counter() - mermaid_start) * 1000)
        timings["total"] = int((time.perf_counter() - start) * 1000)
        return GenerateResponse(transcript=final_transcript, graph=graph, mermaid=mermaid, timings_ms=timings)

    async def _resolve_transcript(
        self,
        *,
        audio_bytes: bytes | None,
        audio_filename: str | None,
        audio_content_type: str | None,
        transcript: str | None,
    ) -> str:
        manual = (transcript or "").strip()
        if manual:
            return manual
        if not audio_bytes:
            return "用户描述了一个由输入数据、语音转写、草图识别、语义融合和方法图输出组成的科研流程。"
        max_bytes = self.settings.max_audio_mb * 1024 * 1024
        if len(audio_bytes) > max_bytes:
            raise ValueError(f"音频文件超过 {self.settings.max_audio_mb} MB 限制")
        if self.settings.use_mock or not self.client:
            return "示例转写：输入草图和语音说明，经过语音识别、草图解析、多模态语义融合，生成论文风格方法图。"
        try:
            result = self.client.audio.transcriptions.create(
                file=(audio_filename or "audio.webm", audio_bytes, audio_content_type or "audio/webm"),
                model=self.settings.openai_transcribe_model,
                response_format="text",
            )
            return str(result).strip()
        except Exception:
            if self.settings.openai_fallback_to_mock:
                return "语音转写失败，已使用 mock 文本：输入语音和草图，系统识别模块与连接关系并生成方法图。"
            raise

    async def _build_graph(
        self,
        *,
        sketch_bytes: bytes | None,
        sketch_content_type: str | None,
        transcript: str,
    ) -> MethodGraph:
        if self.settings.use_mock or not self.client:
            return self._mock_graph(transcript, warning=None)
        try:
            content: list[dict[str, Any]] = [
                {
                    "type": "input_text",
                    "text": (
                        "请根据以下语音转写和草图生成科研方法图。"
                        f"\n语音转写：{transcript}\n"
                        "如果草图为空白，请主要依据文本。"
                    ),
                }
            ]
            image_url = self._image_data_url(sketch_bytes, sketch_content_type)
            if image_url:
                content.append({"type": "input_image", "image_url": image_url})

            response = self.client.responses.parse(
                model=self.settings.openai_graph_model,
                instructions=SYSTEM_PROMPT,
                input=[{"role": "user", "content": content}],
                text_format=MethodGraph,
                store=False,
            )
            parsed = response.output_parsed
            if not parsed:
                raise ValueError("OpenAI 未返回结构化图")
            return parsed
        except Exception as exc:
            if self.settings.openai_fallback_to_mock:
                return self._mock_graph(transcript, warning=f"OpenAI 图结构化失败，已回退 mock：{type(exc).__name__}")
            raise

    def _image_data_url(self, sketch_bytes: bytes | None, sketch_content_type: str | None) -> str | None:
        if not sketch_bytes:
            return None
        try:
            # 重新编码为 PNG，避免浏览器 canvas 或上传图片带来不一致格式。
            image = Image.open(BytesIO(sketch_bytes)).convert("RGBA")
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            payload = base64.b64encode(buffer.getvalue()).decode("ascii")
            return f"data:image/png;base64,{payload}"
        except Exception:
            payload = base64.b64encode(sketch_bytes).decode("ascii")
            content_type = sketch_content_type or "image/png"
            return f"data:{content_type};base64,{payload}"

    def _mock_graph(self, transcript: str, warning: str | None) -> MethodGraph:
        warnings = ["当前运行在 mock 模式，结果用于课堂演示与接口验证。"]
        if warning:
            warnings.append(warning)
        lowered = transcript.lower()
        if "卷积神经网络" in transcript or "卷积核" in transcript or "softmax" in lowered:
            return MethodGraph(
                title="卷积神经网络讲解",
                summary="样例展示 CNN 从输入图像到分类输出的核心处理链路。",
                nodes=[
                    GraphNode(id="input_image", label="输入图像", type="input"),
                    GraphNode(id="kernel", label="卷积核", type="model"),
                    GraphNode(id="feature_map", label="特征图", type="process"),
                    GraphNode(id="relu", label="ReLU", type="process"),
                    GraphNode(id="pooling", label="池化", type="process"),
                    GraphNode(id="stacked_conv", label="多层卷积", type="model"),
                    GraphNode(id="flatten", label="Flatten", type="process"),
                    GraphNode(id="fc", label="全连接", type="model"),
                    GraphNode(id="softmax", label="Softmax分类", type="output"),
                    GraphNode(id="receptive_field", label="局部感受野", type="note"),
                    GraphNode(id="sharing", label="参数共享", type="note"),
                ],
                edges=[
                    GraphEdge(source="input_image", target="kernel"),
                    GraphEdge(source="kernel", target="feature_map"),
                    GraphEdge(source="feature_map", target="relu"),
                    GraphEdge(source="relu", target="pooling"),
                    GraphEdge(source="pooling", target="stacked_conv"),
                    GraphEdge(source="stacked_conv", target="flatten"),
                    GraphEdge(source="flatten", target="fc"),
                    GraphEdge(source="fc", target="softmax"),
                    GraphEdge(source="receptive_field", target="kernel", type="semantic"),
                    GraphEdge(source="sharing", target="kernel", type="semantic"),
                ],
                warnings=warnings,
                confidence=0.82,
            )
        if "ddpm" in lowered or "latent diffusion" in lowered or "扩散模型" in transcript:
            return MethodGraph(
                title="扩散技术发展路线",
                summary="样例展示扩散模型从 DDPM 到快速采样和强条件控制的发展链路。",
                nodes=[
                    GraphNode(id="ddpm", label="DDPM", type="model"),
                    GraphNode(id="ddim", label="DDIM", type="model"),
                    GraphNode(id="cfg", label="Classifier-Free Guidance", type="process"),
                    GraphNode(id="latent_diffusion", label="Latent Diffusion", type="model"),
                    GraphNode(id="stable_diffusion", label="Stable Diffusion", type="model"),
                    GraphNode(id="controlnet", label="ControlNet", type="model"),
                    GraphNode(id="dit", label="DiT", type="model"),
                    GraphNode(id="consistency", label="Consistency Models", type="model"),
                    GraphNode(id="fast_sampling", label="采样加速", type="metric"),
                    GraphNode(id="text_control", label="文本条件控制", type="process"),
                ],
                edges=[
                    GraphEdge(source="ddpm", target="ddim"),
                    GraphEdge(source="ddim", target="cfg"),
                    GraphEdge(source="cfg", target="text_control", type="semantic"),
                    GraphEdge(source="cfg", target="latent_diffusion"),
                    GraphEdge(source="latent_diffusion", target="stable_diffusion"),
                    GraphEdge(source="stable_diffusion", target="controlnet"),
                    GraphEdge(source="stable_diffusion", target="dit"),
                    GraphEdge(source="dit", target="consistency"),
                    GraphEdge(source="consistency", target="fast_sampling", type="evaluation"),
                ],
                warnings=warnings,
                confidence=0.82,
            )
        if "视频生成" in transcript or "sora" in lowered or "phenaki" in lowered:
            return MethodGraph(
                title="视频生成模型发展脉络",
                summary="样例展示视频生成从早期帧预测到时空 Transformer 和长视频系统的演进。",
                nodes=[
                    GraphNode(id="early_video", label="早期GAN/RNN视频", type="model"),
                    GraphNode(id="frame_prediction", label="帧预测", type="process"),
                    GraphNode(id="video_diffusion", label="Video Diffusion Models", type="model"),
                    GraphNode(id="imagen_video", label="Imagen Video", type="model"),
                    GraphNode(id="phenaki", label="Phenaki", type="model"),
                    GraphNode(id="videoldm", label="VideoLDM", type="model"),
                    GraphNode(id="spacetime_transformer", label="时空Transformer", type="model"),
                    GraphNode(id="lumiere", label="Lumiere", type="model"),
                    GraphNode(id="sora", label="Sora", type="model"),
                    GraphNode(id="temporal_consistency", label="时序一致性", type="metric"),
                    GraphNode(id="long_video", label="长视频生成", type="output"),
                    GraphNode(id="text_to_video", label="文本到视频", type="process"),
                ],
                edges=[
                    GraphEdge(source="early_video", target="frame_prediction"),
                    GraphEdge(source="frame_prediction", target="video_diffusion"),
                    GraphEdge(source="video_diffusion", target="imagen_video"),
                    GraphEdge(source="video_diffusion", target="phenaki"),
                    GraphEdge(source="imagen_video", target="text_to_video", type="semantic"),
                    GraphEdge(source="phenaki", target="long_video", type="semantic"),
                    GraphEdge(source="video_diffusion", target="videoldm"),
                    GraphEdge(source="videoldm", target="spacetime_transformer"),
                    GraphEdge(source="spacetime_transformer", target="lumiere"),
                    GraphEdge(source="spacetime_transformer", target="sora"),
                    GraphEdge(source="sora", target="temporal_consistency", type="evaluation"),
                ],
                warnings=warnings,
                confidence=0.82,
            )
        if "预处理" in transcript or "分类" in transcript:
            return MethodGraph(
                title="线性实验流程",
                summary="样例展示从输入数据到模型输出的线性科研流程。",
                nodes=[
                    GraphNode(id="input_data", label="输入数据", type="input"),
                    GraphNode(id="preprocess", label="预处理", type="process"),
                    GraphNode(id="model", label="深度学习模型", type="model"),
                    GraphNode(id="result", label="分类结果", type="output"),
                ],
                edges=[
                    GraphEdge(source="input_data", target="preprocess"),
                    GraphEdge(source="preprocess", target="model"),
                    GraphEdge(source="model", target="result"),
                ],
                warnings=warnings,
                confidence=0.78,
            )
        if "结构还原度" in transcript or "主观评分" in transcript:
            return MethodGraph(
                title="方法图评测闭环",
                summary="样例展示生成、用户检查、指标评测和反馈迭代。",
                nodes=[
                    GraphNode(id="graph", label="方法图", type="output"),
                    GraphNode(id="check", label="用户检查", type="process"),
                    GraphNode(id="structure", label="结构还原度", type="metric"),
                    GraphNode(id="latency", label="生成耗时", type="metric"),
                    GraphNode(id="score", label="主观评分", type="metric"),
                    GraphNode(id="feedback", label="反馈迭代", type="process"),
                ],
                edges=[
                    GraphEdge(source="graph", target="check"),
                    GraphEdge(source="check", target="structure", type="evaluation"),
                    GraphEdge(source="check", target="latency", type="evaluation"),
                    GraphEdge(source="check", target="score", type="evaluation"),
                    GraphEdge(source="score", target="feedback", type="feedback"),
                ],
                warnings=warnings,
                confidence=0.78,
            )
        if "asr" in lowered or "mermaid" in lowered or "语义融合" in transcript:
            return MethodGraph(
                title="语音草图多模态方法图生成流程",
                summary="样例展示语音、草图、转写、结构识别和语义融合。",
                nodes=[
                    GraphNode(id="voice", label="语音描述", type="input"),
                    GraphNode(id="sketch", label="手绘草图", type="input"),
                    GraphNode(id="asr", label="ASR 转写", type="process"),
                    GraphNode(id="structure", label="结构识别", type="process"),
                    GraphNode(id="fusion", label="语义融合", type="fusion"),
                    GraphNode(id="mermaid", label="Mermaid 方法图", type="output"),
                ],
                edges=[
                    GraphEdge(source="voice", target="asr"),
                    GraphEdge(source="sketch", target="structure"),
                    GraphEdge(source="asr", target="fusion"),
                    GraphEdge(source="structure", target="fusion"),
                    GraphEdge(source="fusion", target="mermaid"),
                ],
                warnings=warnings,
                confidence=0.8,
            )

        nodes = [
            GraphNode(id="voice", label="语音描述", type="input", description="用户口头解释研究流程"),
            GraphNode(id="sketch", label="手绘草图", type="input", description="白板或画布中的粗略结构"),
            GraphNode(id="asr", label="语音转写", type="process", description="把音频转成可编辑文本"),
            GraphNode(id="sketch_parse", label="草图解析", type="process", description="识别框、箭头和空间关系"),
            GraphNode(id="fusion", label="语义融合", type="fusion", description="对齐语音语义与草图结构"),
            GraphNode(id="graph", label="结构化方法图", type="output", description="输出节点、边和 Mermaid"),
        ]
        if any(token in lowered for token in ["metric", "指标", "评测", "accuracy", "wer", "cer"]):
            nodes.append(GraphNode(id="eval", label="效果评测", type="metric", description="计算准确率、结构还原度和耗时"))
        edges = [
            GraphEdge(source="voice", target="asr", label="转写"),
            GraphEdge(source="sketch", target="sketch_parse", label="识别"),
            GraphEdge(source="asr", target="fusion", label="语义"),
            GraphEdge(source="sketch_parse", target="fusion", label="结构"),
            GraphEdge(source="fusion", target="graph", label="生成"),
        ]
        if any(node.id == "eval" for node in nodes):
            edges.append(GraphEdge(source="graph", target="eval", label="验证", type="evaluation"))
        return MethodGraph(
            title="语音草图多模态方法图生成流程",
            summary="系统把口头描述和手绘草图融合为结构化方法图，降低科研早期想法整理成本。",
            nodes=nodes,
            edges=edges,
            warnings=warnings,
            confidence=0.72,
        )
