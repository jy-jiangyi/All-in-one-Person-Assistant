import gradio as gr
from data import db  # 数据库逻辑在 data/db.py 中
from azure_chatgpt import AzureChatGPT
from user_guidance import user_guidance
from voice_input import another_function
from user_mental_health_dashboard import plot_anxiety_scale
# 初始化数据库
db.init_db()

# 登录函数
def login(username, password):
    if db.check_user(username, password):
        return "",gr.update(visible=False), gr.update(visible=True), gr.update(visible=True)  # 第4个值用于控制按钮的可见性 # 登录成功，显示主界面
    else:
        return "Invalid username or password.", gr.update(visible=True), gr.update(visible=False), gr.update(visible=False) # 登录失败

# 注册函数
def signup(username, password):
    if db.insert_user(username, password):
        return "Signup successful! Please login.", gr.update(visible=True), gr.update(visible=False)  # 注册成功，跳回登录界面
    else:
        return "Username already exists. Please try a different one.", gr.update(visible=True), gr.update(visible=False)

def logout():
    return gr.update(visible=True), gr.update(visible=False)  # 登出后回到登录界面
def show_module(module):
    """切换功能模块的显示"""
    return (gr.update(visible=(module == "Personal Assessment")),
            gr.update(visible=(module == "Emotional Support")),
            gr.update(visible=(module == "Voice Emotional Support")),
            gr.update(visible=(module == "User mental health dashboard")))
chatgpt = AzureChatGPT()
def chat_interface():
    with gr.Blocks() as chat_demo:
        chatbot = gr.Chatbot()
        with gr.Row():
            with gr.Column(scale=4):
                with gr.Column(scale=50):
                    user_input = gr.Textbox(show_label=False, placeholder="Input...", lines=10, container=False)
                with gr.Column(min_width=32, scale=1):
                    submitBtn = gr.Button("Submit", variant="primary")
            with gr.Column(scale=1):
                emptyBtn = gr.Button("Clear History")
        # 提交问题
        submitBtn.click(predict, [user_input, chatbot], [chatbot], show_progress=True)
        submitBtn.click(reset_user_input, [], [user_input])
        # 清空历史对话
        emptyBtn.click(reset_state, outputs=[chatbot], show_progress=True)

    return chat_demo

def predict(input, chatbot):
    """调用openai接口，获取答案"""
    chatbot.append((input, ""))
    # 找chatgpt要答案
    response = chatgpt.get_response(input)
    chatgpt.save_messages_to_file()
    chatbot[-1] = (input, response)
    return chatbot

def reset_user_input():
    return gr.update(value='')

def reset_state():
    chatgpt.clean_history()
    return []

def main():
    with gr.Blocks() as demo:
        # 登录界面
        with gr.Column(visible=True) as login_interface:
            gr.Markdown("## Please login to continue")
            username = gr.Textbox(placeholder="Username", label="Username")
            password = gr.Textbox(placeholder="Password", type="password", label="Password")
            login_button = gr.Button("Login")
            login_failed = gr.Markdown(value="", visible=True)
            signup_button = gr.Button("Sign up")

        # 注册界面
        with gr.Column(visible=False) as signup_interface:
            gr.Markdown("## Please sign up")
            signup_username = gr.Textbox(placeholder="Username", label="Username")
            signup_password = gr.Textbox(placeholder="Password", type="password", label="Password")
            signup_submit = gr.Button("Submit")
            signup_status = gr.Markdown(value="", visible=True)
            back_to_login_button = gr.Button("Back to login")

        # 主界面，默认隐藏，登录成功后显示
        with gr.Column(visible=False) as main_interface:
            gr.Markdown("## Welcome to the Personal Assistant Dashboard")
            personal_assessment_button = gr.Button("Personal Assessment")
            emotional_support_button = gr.Button("Emotional Support")
            voice_support_button = gr.Button("Voice Emotional Support")
            mental_health_button = gr.Button("User mental health dashboard")
            logout_button = gr.Button("Logout")

        # 各个功能模块界面
        with gr.Column(visible=False) as personal_assessment_interface:
            gr.Markdown("### Personal Assessment Module")
            # 填充个人评估的功能内容
            user_guidance(gr.State(False))
            back_to_dashboard_button1 = gr.Button("Back to Dashboard")

        with gr.Column(visible=False) as emotional_support_interface:
            gr.Markdown("### Emotional Support Module")
            chat_interface()
            back_to_dashboard_button2 = gr.Button("Back to Dashboard")

        with gr.Column(visible=False) as voice_support_interface:
            gr.Markdown("### Voice Emotional Support Module")
            another_function()  # 假设这里是语音支持功能
            back_to_dashboard_button3 = gr.Button("Back to Dashboard")

        with gr.Column(visible=False) as mental_health_interface:
            gr.Markdown("### User Mental Health Dashboard")
            output_image = gr.Image(label="Anxiety Scale Chart")
            refresh_button = gr.Button("Generate Anxiety Scale Chart")
            refresh_button.click(lambda: plot_anxiety_scale(), outputs=output_image)
            back_to_dashboard_button4 = gr.Button("Back to Dashboard")

        # 绑定登录按钮与 login 函数
        # 绑定登录按钮与 login 函数
        login_button.click(
            fn=login, 
            inputs=[username, password],
            outputs=[login_failed, login_interface, main_interface, personal_assessment_button]  # 现在输出4个值
        )


        # 绑定注册按钮与 signup 界面的显示
        signup_button.click(
            fn=lambda: (gr.update(visible=False), gr.update(visible=True)),
            inputs=[],
            outputs=[login_interface, signup_interface]
        )

        # 绑定注册提交按钮与 signup 函数
        signup_submit.click(
            fn=signup,
            inputs=[signup_username, signup_password],
            outputs=[signup_status, signup_interface, login_interface]
        )

        # 绑定“返回登录”按钮
        back_to_login_button.click(
            fn=lambda: (gr.update(visible=True), gr.update(visible=False)),
            inputs=[],
            outputs=[login_interface, signup_interface]
        )

        # 绑定登出按钮与 logout 函数
        logout_button.click(
            fn=logout, 
            inputs=[], 
            outputs=[login_interface, main_interface]
        )

        # 绑定功能按钮与各自的模块显示
        personal_assessment_button.click(
            fn=lambda: show_module("Personal Assessment"),
            inputs=[],
            outputs=[personal_assessment_interface, emotional_support_interface, voice_support_interface, mental_health_interface]
        )

        emotional_support_button.click(
            fn=lambda: show_module("Emotional Support"),
            inputs=[], 
            outputs=[personal_assessment_interface, emotional_support_interface, voice_support_interface, mental_health_interface]
        )

        voice_support_button.click(
            fn=lambda: show_module("Voice Emotional Support"),
            inputs=[], 
            outputs=[personal_assessment_interface, emotional_support_interface, voice_support_interface, mental_health_interface]
        )

        mental_health_button.click(
            fn=lambda: show_module("User mental health dashboard"),
            inputs=[], 
            outputs=[personal_assessment_interface, emotional_support_interface, voice_support_interface, mental_health_interface]
        )

        # 绑定返回按钮与仪表板的显示
        back_to_dashboard_button1.click(
            fn=lambda: show_module(""),
            inputs=[],
            outputs=[personal_assessment_interface, emotional_support_interface, voice_support_interface, mental_health_interface]
        )
        back_to_dashboard_button2.click(
            fn=lambda: show_module(""),
            inputs=[],
            outputs=[personal_assessment_interface, emotional_support_interface, voice_support_interface, mental_health_interface]
        )
        back_to_dashboard_button3.click(
            fn=lambda: show_module(""),
            inputs=[],
            outputs=[personal_assessment_interface, emotional_support_interface, voice_support_interface, mental_health_interface]
        )
        back_to_dashboard_button4.click(
            fn=lambda: show_module(""),
            inputs=[],
            outputs=[personal_assessment_interface, emotional_support_interface, voice_support_interface, mental_health_interface]
        )

    demo.launch(share=False, inbrowser=True)

if __name__ == '__main__':
    main()