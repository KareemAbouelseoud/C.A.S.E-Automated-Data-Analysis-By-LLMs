primary_button="""
                    <style>
                    .element-container:has(#button-after) + div button {
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
                        padding: 30px;
                        font-size: 50px;
                        text-align: center;
                        cursor: pointer;
                        justify-content: center;
                        align-items: center;
                        margin-bottom: 20px; /* Adds vertical space if wrapping occurs */
                        transition: box-shadow 0.3s ease; /* Smooth transition */
                        border: none; /* Explicitly remove any border */

                        }
                        .element-container:has(#button-after) + div button:hover {
                        box-shadow: 
                            0 0 10px rgba(255, 255, 255, 0.6), 
                            0 0 20px rgba(255, 255, 255, 0.5), 
                            0 0 30px rgba(255, 255, 255, 1); /* Stronger glow on hover */
                    }
                    </style>
                    """
back_button= """
                    <style>
                    .element-container:has(#button-back) + div button {
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
                        text-align: center;
                        cursor: pointer;
                        padding: 0px;
                        justify-content: center;
                        align-items: center;
                        margin-bottom: 5px; /* Adds vertical space if wrapping occurs */
                        transition: box-shadow 0.3s ease; /* Smooth transition */
                        border: none; /* Explicitly remove any border */

                        }
                        .element-container:has(#button-back) + div button:hover {
                        box-shadow: 
                            0 0 10px rgba(255, 255, 255, 0.6), 
                            0 0 20px rgba(255, 255, 255, 0.5), 
                            0 0 30px rgba(255, 255, 255, 1); /* Stronger glow on hover */
                    }
                    </style>
                """
segmented_button= """
                    <style>
                    .element-container:has(#button-segmented) + div button {
                        justify-content: center;
                        align-items: center;
                        background: rgba(0, 0, 0, 0.4);
                        z-index: 2;
                        color: white;
                        font-size: 50px;
                        text-align: center;
                        cursor: pointer;
                        transition: box-shadow 0.3s ease; /* Smooth transition */
                        border: none; /* Explicitly remove any border */
                        }
                        .element-container:has(#button-segmented) + div button:hover {
                        box-shadow: 
                            0 0 10px rgba(255, 255, 255, 0.6), 
                            0 0 20px rgba(255, 255, 255, 0.5), 
                            0 0 30px rgba(255, 255, 255, 1); /* Stronger glow on hover */
                    }
                    .st-emotion-cache-1u8vu9t {
                                box-shadow: 
                                    0 0 10px rgba(0, 255, 255, 0.6), 
                                    0 0 20px rgba(0, 255, 255, 0.5), 
                                    0 0 30px rgba(0, 255, 255, 1); /* Electric blue on click */
                                border: none; /* Explicitly remove any border */
                            }
                    </style>
                """
rounded_button=  f"""
        <style>
        div.stButton > button:first-child {{ border-radius:15px 15px 15px 15px;}}

        <style>
        """

sidebar_button="""
                    <style>
                    .element-container:has(#button-sidebar) + div button {
                        justify-content: center;
                        align-items: center;
                        width: 60%; /* Ensure the container takes up full width */
                        border-radius: 16px;
                        background: rgba(0, 0, 0, 0.4);
                        box-shadow: 
                            0 0 6px rgba(255, 255, 255, 0.3), 
                            0 0 12px rgba(255, 255, 255, 0.2), 
                            0 0 18px rgba(255, 255, 255, 0.2);
                        color: white;
                        padding: 20px;
                        margin-left: 45px; /* Adds left margin */
                        margin-right: 10px; /* Adds right margin */
                        transition: box-shadow 0.3s ease; /* Smooth transition */
                        border: none; /* Explicitly remove any border */

                        }
                        .element-container:has(#button-sidebar) + div button:hover {
                        box-shadow: 
                            0 0 10px rgba(255, 255, 255, 0.6), 
                            0 0 20px rgba(255, 255, 255, 0.5), 
                            0 0 30px rgba(255, 255, 255, 1); /* Stronger glow on hover */
                    }
                    </style>
                    """
project_button="""
                <style>
                .element-container:has(#button-after-{first}) + div button {{
                border-radius: 16px;
                background: rgba(0, 0, 0, 0.4);
                z-index: 2;
                box-shadow: 
                    0 0 6px rgba(255, 255, 255, 0.3), 
                    0 0 12px rgba(255, 255, 255, 0.2), 
                    0 0 18px rgba(255, 240, 200, 0.4); /* Initial glow */
                color: white;
                width: 100%; /* Ensure the container takes up full width */
                height: 100%; /* Optional: to ensure vertical centering */
                padding: 50px;
                font-size: 20px;
                text-align: center;
                cursor: pointer;
                justify-content: center;
                align-items: center;
                text-align: center;
                margin-top: 20px;
                transition: box-shadow 0.3s ease; /* Smooth transition */
                border: none; /* Explicitly remove any border */
                    }}
                    .element-container:has(#button-after-{second}) + div button:hover {{
                    box-shadow: 
                    0 0 10px rgba(255, 255, 255, 0.6), 
                    0 0 20px rgba(255, 255, 255, 0.5), 
                    0 0 30px rgba(255, 240, 130, 1); /* Initial glow */
                }}
                </style>
"""