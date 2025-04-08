tab_design="""
    <style>
        [data-baseweb="tab-highlight"] {
            background-color: rgba(255, 240, 200, 0.4);
            box-shadow: 
                    0 0 6px rgba(255, 255, 255, 1), 
                    0 0 12px rgba(255, 255, 255, 1), 
                    0 0 18px rgba(255, 255, 255, 1); /* Initial glow */

                            }

	.stTabs [data-baseweb="tab"] {
        color: white;
        text-shadow: 0 0 1px white, 0 0 1px white, 0 0 1px white;

    }
                    
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center; /* Center horizontally */
        align-items: center; /* Center vertically */
    }

    </style>
"""
expander="""
            <style>
        .stExpander {
            justify-content: center;
                        align-items: center;
                        width: 100%; /* Ensure the container takes up full width */
                        height: 100%; /* Optional: to ensure vertical centering */
                        border-radius: 16px;
                        background: rgba(0, 0, 0, 0.4);
                        z-index: 2;
                        box-shadow: 
                            0 0 6px rgba(255, 255, 255, 0.3), 
                            0 0 12px rgba(255, 255, 255, 0.2), 
                            0 0 18px rgba(255, 255, 255, 0.2);
                        color: white;
                        font-size: 50px;
                        cursor: pointer;
                        padding: 0px;
                        justify-content: center;
                        align-items: center;
                        margin-bottom: 5px; /* Adds vertical space if wrapping occurs */
                        transition: box-shadow 0.3s ease; /* Smooth transition */
                        border: none; /* Explicitly remove any border */

        }
        .stExpander:hover {
            box-shadow: 
                0 0 10px rgba(255, 255, 255, 0.6), 
                0 0 20px rgba(255, 255, 255, 0.5), 
                0 0 30px rgba(255, 255, 255, 1); /* Stronger glow on hover */
        }
        .st-emotion-cache-8s6zi3.enj44ev3:hover {
            color: white;
            text-shadow: 
                0 0 10px rgba(255, 255, 255, 0.6), 
                0 0 20px rgba(255, 255, 255, 0.5), 
                0 0 30px rgba(255, 255, 255, 1); /* Stronger glow on hover */
        }
        .e14lo1l1.st-emotion-cache-1b2ybts.ex0cdmw0:hover svg {
            fill: white;
            transition: fill 0.3s ease; /* Smooth transition */
        }
    </style>
    """
logo="""
                    <style>
                    [data-testid="stLogo"] {
                        width: 500;  /* Adjust width as needed */
                        height: auto;  /* Maintain aspect ratio *

                """ 
background='''
                <style>
                [data-testid="stHeader"] {
                    background-color: rgba(0,0,0,0);
                }
                [data-testid="stAppViewContainer"] {
                    background: url("app/static/imagemeshgradient.png") no-repeat center center fixed;
                    background-size: cover;
                    opacity: 1;
                    box-shadow: 0 0 10px rgba(255, 255, 255, 0.5), 0 0 20px rgba(255, 255, 255, 0.5), 0 0 30px rgba(255, 255, 255, 0.5);
                }
                .st-emotion-cache-lr2bj0.eiemyj5,.st-emotion-cache-qcpnpn.eiemyj5 {
                    border-radius: 16px;
                    background: rgba(0,0,0,0.5);
                    z-index: 2;
                    box-shadow: 0 0 10px rgba(255, 255, 255, 0.5), 0 0 20px rgba(255, 255, 255, 0.5), 0 0 30px rgba(255, 255, 255, 0.5);
                }
                .stSidebar {
                    background: url("app/static/background final 2.png") no-repeat center center;
                    background-size: cover;
                    opacity: 1;
                    box-shadow: 0 0 10px rgba(255, 255, 255, 0.5), 0 0 20px rgba(255, 255, 255, 0.5), 0 0 30px rgba(255, 255, 255, 0.5);
                    }
                </style>
                '''
select_box = """
    <style>
    </style>
"""
dialog_box="""
 <style>
    /* Dialog box dimensions override */
    [role="dialog"] {
        width:80vw !important; /* Set the width to 50% of the viewport */
        background: rgba(0, 0, 0, 1);
        z-index: 2;
        box-shadow: 
            0 0 6px rgba(255, 255, 255, 0.3), 
            0 0 12px rgba(255, 255, 255, 0.2), 
            0 0 18px rgba(255, 255, 255, 0.2);
        color: white;
        padding: 30px;
        font-size: 50px;
        text-align: center;
        cursor: pointer;
        
        align-items: center;
        margin-bottom: 20px; /* Adds vertical space if wrapping occurs */
        transition: box-shadow 0.3s ease; /* Smooth transition */
        border: none; /* Explicitly remove any border */
        height: 86vh !important; /* Set the height to 50% of the viewport */
    }

    /* Dialog content area */
    
    
    
            .chat-message {
                text-size-adjust: 100%;
                -webkit-font-smoothing: auto;
                -webkit-tap-highlight-color: transparent;
                user-select: text;
                pointer-events: all;
                font-weight: normal;
                line-height: 1.6;
                font-family: "Source Sans Pro", sans-serif;
                font-size: 1rem;
                color: inherit;
                box-sizing: border-box;
                inline-size: fit-content;
                padding: 10px;
                border-radius: 15px;
                margin: 5px 0;
                background-color: #262730;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                word-wrap: break-word;
                padding-right: 39px !important;
            }
            .stTextArea textarea {
    text-size-adjust: 100%;
    -webkit-font-smoothing: auto;
    -webkit-tap-highlight-color: transparent;
    user-select: text;
    pointer-events: all;
    font-family: "Source Sans Pro", sans-serif;
    font-size: 1rem;
    font-weight: normal;
    padding-top: 1rem;
    padding-right: 1rem;
    padding-bottom: 1rem;
    padding-left: 1rem;
    width: 100%;
    box-sizing: border-box;
    color: rgb(255, 246, 236);
    outline: none;
    min-width: 0px;
    max-width: 100%;
    cursor: text;
    margin: 0px;
    line-height: 1.4;
    caret-color: rgb(255, 246, 236);
    resize: vertical;
    min-height: 4.25rem;
    background: rgb(19, 19, 22);
    border: none !important;
    height: 71vh !important;
}

div[data-baseweb="textarea"]:nth-of-type(2),
div[data-baseweb="textarea"]:nth-child(2){
    position: static !important;
    border: none !important;
}
.stVerticalBlock.st-emotion-cache-t85rj.eiemyj3{
    top: -113px !important;
    border-top-right-radius: 1rem;
    border-bottom-right-radius: 1rem;
    width: 58vw;
    height: 85.8vh;
    background:rgb(19, 19, 22);
    position:absolute;
}
.stVerticalBlock.st-emotion-cache-p6f4r1.eiemyj3 {
    position: relative !important;
    left: -24px !important;
}
div[data-testid="stChatInput"] textarea {
        box-sizing: border-box;
        bottom: 5px ;
        position: fixed;
        z-index: 1000; 
    }
    div[data-baseweb="textarea"]:first-of-type {
        box-sizing: border-box;
        bottom: 5px ;
        position: fixed;
        z-index: 1000;
        background-color: #222222; 
    }
    div[data-baseweb="toaster"] {
        
        z-index: 1000041;
        top:12vh;
        
    }
    button[data-testid="stChatInputSubmitButton"] {
        bottom: 5px ;
        position: fixed;
        z-index: 1000;
    }
    .st-emotion-cache-1pqiyj1.ekr3hml7 {
        background: url("app/static/imagemeshgradient.png") no-repeat center center fixed;
        background-position: center 200px;
            }
.chat-history-container {
    max-height:55vh;
    overflow-y: auto; /* Enables scrolling */
    padding: 1rem;
    margin-bottom: 60px;
    background: rgba(0, 0, 0, 0.2);
    border-radius: 10px;
    display: flex;
    flex-direction: column;
}

.chat-message {
    margin: 8px 0;
    padding: 12px;
    border-radius: 8px;
    max-width: 90%;
    word-wrap: break-word;
}

.user-message {
    background: rgb(55, 55, 65);
    margin-left: auto;
    margin-right: 0;
}

.assistant-message {
    background: rgb(45, 45, 55);
    margin-right: auto;
    margin-left: 0;
}

.chat-history-container::-webkit-scrollbar {
    width: 6px;
}

.chat-history-container::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.1);
}

.chat-history-container::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 3px;
}

/* Ensure the last message is always visible */
.chat-history-container::-webkit-scrollbar-thumb:vertical {
    height: 6px;
    background-color: rgba(255, 255, 255, 0.5);
}


            </style>
"""
