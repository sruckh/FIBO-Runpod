#!/usr/bin/env python3
"""
FIBO RunPod Gradio Interface
Complete interface for Generate, Refine, and Inspire modes
"""
import os
import subprocess
import tempfile
import json
from pathlib import Path
import gradio as gr

# Aspect ratio to resolution mapping (format: "WIDTH HEIGHT")
ASPECT_TO_RESOLUTION = {
    "1:1": "1024 1024",
    "2:3": "832 1248",
    "3:2": "1248 832",
    "3:4": "896 1152",
    "4:3": "1152 896",
    "4:5": "896 1088",
    "5:4": "1088 896",
    "9:16": "768 1344",
    "16:9": "1344 768",
}

def run_generate(prompt, model_mode, seed, steps, aspect_ratio, negative_prompt, guidance_scale):
    """Generate image from text prompt"""
    try:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            output_path = tmp.name

        # FIBO automatically creates {output_path}.json with structured prompt
        json_output_path = output_path + ".json"

        cmd = ["python", "generate.py", "--prompt", prompt, "--output", output_path]

        if model_mode:
            cmd.extend(["--model-mode", model_mode])
        if seed is not None:
            cmd.extend(["--seed", str(int(seed))])
        if steps is not None:
            cmd.extend(["--steps", str(int(steps))])
        if aspect_ratio and aspect_ratio in ASPECT_TO_RESOLUTION:
            resolution = ASPECT_TO_RESOLUTION[aspect_ratio]
            cmd.extend(["--resolution", resolution])
        if negative_prompt and negative_prompt.strip():
            cmd.extend(["--negative-prompt", negative_prompt])
        if guidance_scale is not None:
            cmd.extend(["--guidance-scale", str(guidance_scale)])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            return None, f"❌ Error:\n{result.stderr}", ""

        # Read structured JSON from file if it exists
        structured_json = ""
        try:
            if os.path.exists(json_output_path):
                with open(json_output_path, 'r') as f:
                    structured_json = f.read()
                os.unlink(json_output_path)
        except Exception as e:
            # Fallback: try to extract from stdout
            try:
                start = result.stdout.find("{")
                if start != -1:
                    # Find matching closing brace
                    brace_count = 0
                    for i, char in enumerate(result.stdout[start:]):
                        if char == "{":
                            brace_count += 1
                        elif char == "}":
                            brace_count -= 1
                            if brace_count == 0:
                                structured_json = result.stdout[start:start + i + 1]
                                # Pretty print the JSON
                                import json as json_lib
                                structured_json = json_lib.dumps(json_lib.loads(structured_json), indent=2)
                                break
            except:
                pass

        return output_path, f"✅ Generated successfully!\n\n{result.stdout}", structured_json

    except subprocess.TimeoutExpired:
        return None, "⏱️ Timeout: Generation took >5 minutes", ""
    except Exception as e:
        return None, f"❌ Error: {str(e)}", ""

def run_refine(source_image, structured_prompt_json, refinement_prompt, seed):
    """Refine existing image using structured prompt + refinement instruction"""
    try:
        # If source image provided, use image-to-image mode
        # Otherwise, use structured prompt refinement mode

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            output_path = tmp.name

        # FIBO automatically creates {output_path}.json with structured prompt
        json_output_path = output_path + ".json"

        cmd = ["python", "generate.py", "--output", output_path]

        # If source image is provided, use it as reference
        if source_image and os.path.exists(source_image):
            cmd.extend(["--image-path", source_image])

        # If structured JSON is provided, save it and use it
        json_path = None
        if structured_prompt_json and structured_prompt_json.strip():
            with tempfile.NamedTemporaryFile(mode='w', suffix=".json", delete=False) as tmp_json_input:
                tmp_json_input.write(structured_prompt_json)
                json_path = tmp_json_input.name
            cmd.extend(["--structured-prompt", json_path])

        # Add refinement prompt if provided
        if refinement_prompt and refinement_prompt.strip():
            cmd.extend(["--prompt", refinement_prompt])

        if seed is not None:
            cmd.extend(["--seed", str(int(seed))])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        # Cleanup temp files
        try:
            if json_path:
                os.unlink(json_path)
        except:
            pass

        if result.returncode != 0:
            return None, f"❌ Error:\n{result.stderr}", ""

        # Read structured JSON from file if it exists
        structured_json = ""
        try:
            if os.path.exists(json_output_path):
                with open(json_output_path, 'r') as f:
                    structured_json = f.read()
                os.unlink(json_output_path)
        except Exception as e:
            # Fallback: try to extract from stdout
            try:
                start = result.stdout.find("{")
                if start != -1:
                    brace_count = 0
                    for i, char in enumerate(result.stdout[start:]):
                        if char == "{":
                            brace_count += 1
                        elif char == "}":
                            brace_count -= 1
                            if brace_count == 0:
                                structured_json = result.stdout[start:start + i + 1]
                                import json as json_lib
                                structured_json = json_lib.dumps(json_lib.loads(structured_json), indent=2)
                                break
            except:
                pass

        return output_path, f"✅ Refined successfully!\n\n{result.stdout}", structured_json

    except subprocess.TimeoutExpired:
        return None, "⏱️ Timeout: Refinement took >5 minutes", ""
    except Exception as e:
        return None, f"❌ Error: {str(e)}", ""

def run_inspire(reference_image, prompt, seed):
    """Generate structured prompt from reference image"""
    try:
        # reference_image is already a file path from gr.Image with type="filepath"
        if not reference_image or not os.path.exists(reference_image):
            return "❌ Error: No image provided or file not found", ""

        # Need an output path for FIBO (it creates {output}.json automatically)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            output_path = tmp.name

        # FIBO automatically creates {output_path}.json with structured prompt
        json_output_path = output_path + ".json"

        cmd = ["python", "generate.py", "--image-path", reference_image, "--output", output_path]

        if prompt and prompt.strip():
            cmd.extend(["--prompt", prompt])
        if seed is not None:
            cmd.extend(["--seed", str(int(seed))])

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            return f"❌ Error:\n{result.stderr}", ""

        # Read structured JSON from file if it exists
        structured_json = ""
        try:
            if os.path.exists(json_output_path):
                with open(json_output_path, 'r') as f:
                    structured_json = f.read()
                os.unlink(json_output_path)
        except Exception as e:
            # Fallback: try to extract from stdout
            try:
                start = result.stdout.find("{")
                if start != -1:
                    brace_count = 0
                    for i, char in enumerate(result.stdout[start:]):
                        if char == "{":
                            brace_count += 1
                        elif char == "}":
                            brace_count -= 1
                            if brace_count == 0:
                                structured_json = result.stdout[start:start + i + 1]
                                import json as json_lib
                                structured_json = json_lib.dumps(json_lib.loads(structured_json), indent=2)
                                break
            except:
                pass

        return f"✅ Prompt extracted successfully!\n\n{result.stdout}", structured_json

    except subprocess.TimeoutExpired:
        return "⏱️ Timeout: Inspire took >5 minutes", ""
    except Exception as e:
        return f"❌ Error: {str(e)}", ""

# Create Gradio interface
with gr.Blocks(title="FIBO Text-to-Image", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🎨 FIBO - Text-to-Image Generator")
    gr.Markdown("8B parameter JSON-native controllable image generation | [GitHub](https://github.com/Bria-AI/FIBO)")

    with gr.Tabs():
        # GENERATE TAB
        with gr.Tab("Generate"):
            gr.Markdown("### Generate new images from text prompts")

            with gr.Row():
                with gr.Column(scale=1):
                    gen_prompt = gr.Textbox(
                        label="Prompt",
                        placeholder="A serene lake at sunset with mountains in the background...",
                        lines=4
                    )

                    with gr.Row():
                        gen_model_mode = gr.Radio(
                            choices=["gemini", "local"],
                            value="gemini",
                            label="VLM Mode (Gemini requires GOOGLE_API_KEY)"
                        )
                        gen_seed = gr.Number(
                            label="Seed (Optional: for reproducibility)",
                            value=None,
                            precision=0
                        )

                    with gr.Accordion("Advanced Settings", open=False):
                        gen_steps = gr.Slider(
                            minimum=20,
                            maximum=100,
                            value=50,
                            step=1,
                            label="Steps"
                        )
                        gen_aspect = gr.Dropdown(
                            choices=["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9"],
                            value="1:1",
                            label="Aspect Ratio (converts to resolution automatically)"
                        )
                        gen_negative = gr.Textbox(
                            label="Negative Prompt",
                            placeholder="blurry, low quality, distorted...",
                            lines=2
                        )
                        gen_guidance = gr.Slider(
                            minimum=1,
                            maximum=20,
                            value=5,
                            step=0.5,
                            label="Guidance Scale"
                        )

                    gen_btn = gr.Button("🎨 Generate Image", variant="primary")

                with gr.Column(scale=1):
                    gen_image = gr.Image(label="Generated Image", type="filepath")
                    gen_status = gr.Textbox(label="Status", lines=8)
                    gen_structured = gr.Code(
                        label="Structured Prompt (JSON)",
                        language="json",
                        lines=6,
                        interactive=False
                    )

            gen_btn.click(
                fn=run_generate,
                inputs=[gen_prompt, gen_model_mode, gen_seed, gen_steps, gen_aspect, gen_negative, gen_guidance],
                outputs=[gen_image, gen_status, gen_structured]
            )

        # REFINE TAB
        with gr.Tab("Refine"):
            gr.Markdown("### Refine existing images with new instructions")
            gr.Markdown("**Option 1:** Upload a source image to refine  \n**Option 2:** Use structured JSON from Generate tab  \n**Option 3:** Use both for maximum control")

            with gr.Row():
                with gr.Column(scale=1):
                    refine_source = gr.Image(
                        label="Source Image (Optional - upload from Generate tab or other source)",
                        type="filepath",
                        sources=["upload", "clipboard"]
                    )
                    refine_json = gr.Code(
                        label="Structured Prompt (JSON, Optional - paste from Generate tab)",
                        language="json",
                        lines=8
                    )
                    refine_prompt = gr.Textbox(
                        label="Refinement Instruction (describe modifications)",
                        placeholder="Make the sky more dramatic with clouds...",
                        lines=3
                    )
                    refine_seed = gr.Number(
                        label="Seed",
                        value=None,
                        precision=0
                    )

                    refine_btn = gr.Button("✨ Refine Image", variant="primary")

                with gr.Column(scale=1):
                    refine_image = gr.Image(label="Refined Image", type="filepath")
                    refine_status = gr.Textbox(label="Status", lines=8)
                    refine_structured = gr.Code(
                        label="Updated Structured Prompt",
                        language="json",
                        lines=6,
                        interactive=False
                    )

            refine_btn.click(
                fn=run_refine,
                inputs=[refine_source, refine_json, refine_prompt, refine_seed],
                outputs=[refine_image, refine_status, refine_structured]
            )

        # INSPIRE TAB
        with gr.Tab("Inspire"):
            gr.Markdown("### Extract structured prompt from reference image")
            gr.Markdown("**Upload an image to extract its structured representation**")

            with gr.Row():
                with gr.Column(scale=1):
                    inspire_image = gr.Image(
                        label="Reference Image",
                        type="filepath",
                        sources=["upload", "clipboard"]
                    )
                    inspire_prompt = gr.Textbox(
                        label="Additional Prompt (Optional - guide extraction)",
                        placeholder="Focus on artistic style...",
                        lines=3
                    )
                    inspire_seed = gr.Number(
                        label="Seed",
                        value=None,
                        precision=0
                    )

                    inspire_btn = gr.Button("🔍 Extract Prompt", variant="primary")

                with gr.Column(scale=1):
                    inspire_status = gr.Textbox(label="Status", lines=10)
                    inspire_structured = gr.Code(
                        label="Extracted Structured Prompt",
                        language="json",
                        lines=12,
                        interactive=False
                    )

            inspire_btn.click(
                fn=run_inspire,
                inputs=[inspire_image, inspire_prompt, inspire_seed],
                outputs=[inspire_status, inspire_structured]
            )

    # Footer
    gr.Markdown("---")
    gr.Markdown("""
    **Environment Variables:**
    - `HF_TOKEN` (required): Hugging Face authentication
    - `GOOGLE_API_KEY` (optional): For Gemini VLM mode (faster), otherwise uses local FIBO-VLM

    **Note:** First generation may take longer as models are downloaded.
    """)

if __name__ == "__main__":
    # Configuration from environment
    server_name = os.environ.get("GRADIO_SERVER_NAME", "0.0.0.0")
    server_port = int(os.environ.get("GRADIO_SERVER_PORT", "7860"))
    share = os.environ.get("GRADIO_SHARE", "true").lower() == "true"

    print(f"🚀 Starting FIBO Gradio Interface")
    print(f"   Server: {server_name}:{server_port}")
    print(f"   Share: {share}")

    demo.launch(
        server_name=server_name,
        server_port=server_port,
        share=share
    )
