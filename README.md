# Writing Bot - AI-Powered Article Assistant

An intelligent writing assistant that helps you create, develop, and refine articles using AI. Built with LangGraph and Google's Gemini, this tool provides a conversational interface for writing with real-time research capabilities and file management.

## 🚀 Features

### **AI Writing Assistant**
- **Conversational Interface**: Natural language interaction for writing tasks
- **Real-time Research**: Internet search capabilities for facts, statistics, and current events
- **Smart File Management**: Direct reading and writing of outline.md and article.md files
- **Contextual Understanding**: Reads your current content to provide relevant suggestions

### **Project Structure**
Each article project follows a clean structure:
```
articles/
└── my-article/
    ├── outline.md     # Bullet-point outline
    ├── article.md     # Full article content
    └── references/    # Research materials (optional)
```

### **Writing Capabilities**
- **Outline Development**: Create and refine bullet-point outlines
- **Article Writing**: Transform outlines into full articles
- **Content Evaluation**: Review and suggest improvements
- **Research Integration**: Fact-check and find supporting data

## 🛠️ Installation

1. **Install dependencies**:
   ```bash
   poetry install
   ```

2. **Set up API key**:
   ```bash
   export GOOGLE_API_KEY="your-google-api-key-here"
   ```

3. **Run the assistant**:
   ```bash
   poetry run python cli.py
   ```

## 📝 Usage

### **Starting a Writing Session**
```bash
poetry run python cli.py
```

The assistant will greet you and ask what you'd like to work on. You can:

### **File Operations**
- **Read current content**: "Show me my current outline"
- **Update files**: "Update my outline with these new sections"
- **Append content**: "Add a conclusion section to my article"
- **Insert at specific lines**: "Insert this paragraph at line 10"

### **Research & Writing**
- **Real-time research**: "Research the latest data governance trends"
- **Fact-checking**: "Verify these statistics about AI adoption"
- **Content expansion**: "Expand section 3 with more details"
- **Outline improvement**: "Suggest improvements for my outline structure"

### **Examples**

```bash
# Start the assistant
poetry run python cli.py

# In the conversation, you can say:
"Help me create an outline for an article about data governance"
"Research the latest statistics on AI adoption in healthcare"
"Review my current outline and suggest improvements"
"Expand the introduction section with more background"
"Add a section about best practices to my outline"
"Fact-check the statistics in my article"
```

## 🎯 Core Capabilities

### **1. Outline Development**
- Create hierarchical bullet-point outlines
- Suggest structural improvements
- Add missing sections or details
- Reorganize content flow logically

### **2. Article Writing**
- Transform outlines into full articles
- Expand bullet points into detailed content
- Maintain consistent tone and style
- Ensure logical flow and readability

### **3. Research Integration**
- Real-time internet search for current information
- Fact-checking and verification
- Finding supporting data and examples
- Researching trending topics

### **4. File Management**
- Read and modify outline.md and article.md
- Append or insert content at specific locations
- Work within the secure articles directory
- Automatic backup creation before modifications

## 🔧 Technical Details

### **Dependencies**
- **LangGraph**: Conversational workflow management
- **Google Gemini**: AI content generation and analysis
- **DuckDuckGo**: Real-time internet research
- **File Management**: Secure file operations within articles directory

### **Security**
- All file operations restricted to `writing_bot/articles/` directory
- Automatic backup creation before file modifications
- Safe file reading and writing with proper error handling

### **Architecture**
- **Conversational Interface**: Natural language interaction
- **Tool Integration**: File management and research tools
- **Context Awareness**: Reads current project state
- **Real-time Capabilities**: Live research and fact-checking

## 📚 Writing Guidelines

The assistant follows these principles:
- **Outlines**: Clear, hierarchical bullet points
- **Articles**: Well-structured with proper headings
- **Tone**: Professional and engaging
- **Format**: Proper markdown formatting
- **Flow**: Logical progression and clarity

## 🎉 Getting Started

1. **Install and configure** the tool with your API key
2. **Start a session** with `poetry run python cli.py`
3. **Tell the assistant** what you want to work on
4. **Use natural language** to request help with writing tasks
5. **Let the AI** handle research, suggestions, and file management

The assistant is designed to be your collaborative writing partner, helping you create high-quality articles with real-time research and intelligent suggestions! 