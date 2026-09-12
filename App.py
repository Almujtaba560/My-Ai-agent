import os
import gradio as gr

def create_video(text):
    if not text.strip():
        return "❌ اكتب النص أولاً."

    return f"""✅ تم استلام النص بنجاح!

النص:
{text}

الخطوة التالية: سيتم تحويل النص إلى مشاهد وصوت وفيديو.
"""

demo = gr.Interface(
    fn=create_video,
    inputs=gr.Textbox(
        label="اكتب النص الذي تريد تحويله إلى فيديو",
        lines=8,
        placeholder="اكتب قصتك هنا..."
    ),
    outputs=gr.Textbox(label="النتيجة"),
    title="🎬 AI Text to Video Agent",
    description="وكيل لتحويل النص إلى فيديو"
)

demo.launch()
