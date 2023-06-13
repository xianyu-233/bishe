<template>
    <div class="talk">
        <el-container>
            <!-- 聊天顶部栏 -->
            <el-header class="talk-header">
                    <!-- 右侧图标 -->
                    <div class="talk-header-icon">
                        <!-- 更多 -->
                        <el-icon class="icon">
                            <More />
                        </el-icon>
                        <!-- 关闭 -->
                        <el-icon class="icon">
                            <CloseBold />
                        </el-icon>
                    </div>
            </el-header>
            <!-- main container -->
            <el-container>
                <el-container>
                    <!-- 聊天窗口 -->
                    <el-main class="talk-content">
                        <div v-for="item in contentDiv" :key="item">
                            <div style="margin-top: 20px">
                                <!-- 时间显示 -->
                                <div style="text-align: center;">
                                    <p style="font-size: 1px;color: #9b9b9b;">{{ item.time }}</p>
                                </div>

                                <div style="display: flex;">
                                    <!-- 客户的名字 -->
                                    <div class="name_right" v-if="item.show">
                                        <p style="font-size: 1px;">{{ item.name }}</p>
                                    </div>
                                    <!-- 客户的头像 -->
                                    <div class="url_right" v-if="item.show">
                                        <el-avatar shape="circle" :size="30"></el-avatar>
                                    </div>
                                    <!-- 机器人的头像 -->
                                    <div class="url-left" v-if="!item.show">
                                        <el-avatar shape="circle" :size="30"></el-avatar>
                                    </div>
                                    <!-- 机器人的名字 -->
                                    <div class="name_left" v-if="!item.show">
                                        <p style="font-size: 1px;">{{ item.name }}</p>
                                    </div>


                                </div>

                            </div>


                            <div v-html="item.content" class="content_left" v-if="!item.show">
                            </div>
                            <div v-html="item.content" class="content_right" v-if="item.show">
                            </div>


                        </div>

                    </el-main>

                    <el-footer class="talk-footer">
                        <el-form-item prop="textarea">
                            <!-- 输入框 -->
                            <div class="talk-message">
                                <!-- 表情 -->
                                <!-- <div class="talk-message-face">
                                </div> -->
                                <!-- 输入框 -->
                                <div class="talk-message-content">
                                    <el-input v-model="textarea" :disabled="disabled_input" resize="none" type="text" rows="1" placeholder="请输入要查询的问题" ></el-input>
                                </div>
                                <!-- 发送按钮 -->
                                <div class="talk-message-send">
                                    <el-button 
                                        type="primary" 
                                        style="color:#000000" 
                                        @click="submit()"
                                        :disabled="disabled_button"
                                        >发送</el-button>
                                </div>
                            </div>
                        </el-form-item>
                    </el-footer>
                </el-container>
                <el-aside class="talk-sidebar">侧边栏</el-aside>
            </el-container>

        </el-container>
    </div>

</template>

<script>
import "./assets/talk.css";
import { More } from '@element-plus/icons-vue'
import { CloseBold } from '@element-plus/icons-vue'

export default {
    components: {
        More,
        CloseBold
    },

    data() {
        return {
            // 显示内容
            contentDiv: [],
            // 输入框
            textarea: '',
            // 输入文字
            text: [],
            // 显示哪方的对话变量
            show: false,
            // 显示对话变量
            showflag: true,
            // 后端地址
            address:'http://127.0.0.1:8000/',
            // 回复
            rsp: '',
            // 禁用submit的标志
            disabled_button:true,
            // 等待服务器回复时的禁止标志
            disabled_input:false,
        }
    },
    mounted() {
        this.scrollToBottom()
    },
    watch:{
        // 监视输入框是否有为空
        textarea(){
            if(this.textarea===""||this.textarea===' ')
                this.disabled_button=true
            if(this.textarea!="")
                this.disabled_button=false
        }

    },
    methods: {

        // 让滚动条保持在底部
        scrollToBottom() {
            this.$nextTick(() => {
                let box = this.$el.querySelector(".talk-content")
                box.scrollTop = box.scrollHeight
            })
        },
        fun(){
            this.waitting=!this.waitting;
        },

        // 发送
        submit:function() {
            let text = this.textarea;
            let _this = this
            var time_c = new Date()
            let client = {
                "name": "用户",
                "content": text,
                "show": true,
                "time":time_c
            };
            let serve = {
                "name": "聊天机器人",
                "content": "",
                "show": false,
                "time":""
            };
            // 将输入的内容发去后端
            this.axios({
                methods: 'get',
                url: this.address+this.textarea,
            }).then(function (response) {
                // 等待服务器返回
                console.log(response.data)
                _this.rsp=response.data
                serve.content = _this.rsp
                _this.textarea = "";

                var time_s = new Date()
                serve.time = time_s
                _this.contentDiv.push(serve);
                // 保证滚动条保持在底部
                _this.scrollToBottom();
                //服务器返回后解锁
                _this.disabled_input = false;
            });
            this.contentDiv.push(client);
            // 等待服务器返回时加锁
            this.disabled_input = true;
            _this.scrollToBottom();

        }
    }
}

</script>
