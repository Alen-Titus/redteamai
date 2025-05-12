
from langchain_ollama import ChatOllama
def main():
    print("Hello from security-test!")
 
    llm=ChatOllama(
    model="dolphin-mixtral",
    base_url="13.232.54.218:11434" )
    
    response=llm.invoke("Hello how are you?")
    print(response.content)

if __name__ == "__main__":
    main()
