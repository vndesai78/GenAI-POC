import streamlit as st


from streamlit_option_menu import option_menu


import annualReport, awsAccountplans
st.set_page_config(
        page_title="ChatBot POCs 👍",
)



class MultiApp:

    def __init__(self):
        self.apps = []

    def add_app(self, title, func):

        self.apps.append({
            "title": title,
            "function": func
        })

    def run():
        # app = st.sidebar(
        with st.sidebar:        
            app = option_menu(
                menu_title='GenAI POCs 🔎 ',
                options=['Insights - TML Annual Reports','Insights - AWS Account Plans'],
                icons=['chat-fill','chat-fill'],
                menu_icon='chat-fill',
                default_index=0,
                styles={
                    "container": {"padding": "5!important","background-color":'LightGray',"color":"white","font-size": "20px"},
                    "icon": {"color": "white", "font-size": "23px"}, 
                    "nav-link": {"color":"Black","font-size": "20px", "text-align": "left", "margin":"0px", "--hover-color": "Gray"},
                    "nav-link-selected": {"background-color": "LightGray"},}
                
                )

        
        if app == "Insights - TML Annual Reports":
            annualReport.main()
        if app == "Insights - AWS Account Plans":
            awsAccountplans.main()    
        
             
          
             
    run()            
         
