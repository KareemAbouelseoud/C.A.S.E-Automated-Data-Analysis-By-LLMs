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
        .st-bt, .st-b7, .st-ea {
            background-color: rgb(153 103 190 / 50%);
        }
    .st-hp, .st-gt {
        background-color: rgb(71 51 103 / 85%);
    }
    .st-eu{
        background-color: rgb(200 103 190 / 50%);
        }
    </style>
"""
