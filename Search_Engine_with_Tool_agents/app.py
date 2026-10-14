import os 
import requests
import time 
import streamlit as st
import xml.etree.ElementTree as ET
from urllib.parse import quote
from bs4 import BeautifulSoup
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from dotenv import load_dotenv
load_dotenv()
st.set_page_config(
    page_title= "Wikipedia & Arxiv-Research-Paper Search Engine",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Wikipedia & Arxiv-Research-Paper Search Engine")
st.caption("Wikipedia + Arxiv")

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("GROQ_API_KEY is missing. Add it to your .env file")
    st.stop()

llm=ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    api_key=api_key
)

@tool
def machine_learning_search(query: str)->str:
    """Search Wikipedia for any topic and return article Summaries and URLs."""
    url="https://en.wikipedia.org/w/api.php"

    try:
        response=requests.get(
            url,
            params={
                "action":"query",
                "list":"search",
                "srsearch":query,
                "format":"json",
                "srlimit":3
            },
            headers={
                "User-Agent": "AIResearchAssistant/1.0 (educational project)"
            },
            timeout=30
        )

        response.raise_for_status()

        if not response.text.strip():
            return "Wikipedia returned an empty response. Try again later."

        try:
            data = response.json()
        except ValueError:
            return "Wikipedia returned an invalid response. Please try again."

        results = data.get("query",{}).get("search",[])

        if not results:
            return f"No Wikipedia results found for: {query}"

        output = []

        for item in results:
            title=item.get("title","UnKnown")
            snippet=BeautifulSoup(
                item.get("snippet", ""),"html.parser"
            ).get_text(" ",strip=True)

            article_url =("https://en.wikipedia.org/wiki/"+quote(title.replace(" ","_"),safe="()"))

            output.append(
                f"Title:{title}\n"
                f"Information:{snippet}\n"
                f"Scource:{ article_url}"
            )

        return "\n\n".join(output)
    except requests.exceptions.RequestException as e:
        return f"Wikipedia API/network error: {e}"


@tool
def arxiv_paper_search(query:str)->str:
    """Search arXiv using a paper ID such as 1706.03762 or a research topic."""

    query = query.strip()

    if not query:
        return "Please enter a paper ID or research topic."

    paper_id = query

    if paper_id.lower().startswith("arxiv:"):
        paper_id = paper_id[6:].strip()

    if "/abs/" in paper_id:
        paper_id = paper_id.split("/abs/", 1)[1].strip()

    is_id = (
        "." in paper_id
        and " " not in paper_id
        and "/" not in paper_id
    )

    params = {
        "start": 0,
        "max_results": 1 if is_id else 5
    }

    if is_id:
        params["id_list"] = paper_id
    else:
        params["search_query"] = f'all:"{query}"'
        params["sortBy"] = "relevance"
        params["sortOrder"] = "descending"

    root = None

    for attempt in range(3):
        try:
            response = requests.get(
                "https://export.arxiv.org/api/query",
                params=params,
                headers={
                    "User-Agent": "AIResearchAssistant/1.0"
                },
                timeout=40
            )

            if response.status_code in (429, 500, 502, 503, 504):
                if attempt < 2:
                    time.sleep(3 * (attempt + 1))
                    continue

            response.raise_for_status()

            if not response.content.strip():
                return "arXiv returned an empty response. Try again later."

            root = ET.fromstring(response.content)
            break

        except requests.exceptions.RequestException as e:
            if attempt == 2:
                return (
                    f"arXiv is temporarily unavailable: {e}\n"
                    "Please try again later."
                )
            time.sleep(3 * (attempt + 1))

        except ET.ParseError:
            return "arXiv returned invalid XML. Please try again later."

    if root is None:
        return "Could not retrieve arXiv results."

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    entries = root.findall("atom:entry", ns)

    if not entries:
        return "No arXiv papers found for this query."

    output = []

    for paper in entries:
        title = paper.findtext(
            "atom:title", default="Unknown", namespaces=ns
        ).strip()

        abstract = paper.findtext(
            "atom:summary", default="", namespaces=ns
        ).strip()

        published = paper.findtext(
            "atom:published", default="Unknown", namespaces=ns
        )

        authors = [
            a.findtext("atom:name", default="", namespaces=ns)
            for a in paper.findall("atom:author", ns)
        ]

        url = paper.findtext(
            "atom:id", default="", namespaces=ns
        )

        short_id = url.rstrip("/").split("/")[-1]

        output.append(
            f"Title: {title}\n"
            f"Paper ID: {short_id}\n"
            f"Authors: {', '.join(authors)}\n"
            f"Published: {published[:10]}\n"
            f"Paper URL: {url}\n"
            f"PDF URL: https://arxiv.org/pdf/{short_id}\n"
            f"Abstract: {abstract}"
        )

    return "\n\n---\n\n".join(output)


# ---------------- AGENT ----------------

def create_research_agent(tools):
    return create_agent(
        model=llm,
        tools=tools,
        system_prompt="""
You are an AI research assistant.

For Wikipedia:
- Always use machine_learning_search to retrieve information.
- Explain the topic using clear headings.
- Include an introduction, core concepts, categories,
  applications and key takeaways where relevant.
- Include source links.
- Do not invent facts.

For arXiv:
- Use arxiv_paper_search to retrieve papers.
- Explain the paper details and abstracts clearly.
- Preserve paper titles, IDs, authors, dates and URLs.
- Do not invent research details.

Write readable, well-organized answers.
"""
    )


# ---------------- SIDEBAR ----------------

st.sidebar.title("🔍 Search Options")

option = st.sidebar.selectbox(
    "Choose Search Type",
    [
        "Wikipedia Search",
        "arXiv Paper ID Search",
        "arXiv Topic Search"
    ]
)

# ---------------- INPUT ----------------

if option == "Wikipedia Search":
    query = st.text_input(
        "Enter a Wikipedia topic",
        placeholder="Machine Learning"
    )

elif option == "arXiv Paper ID Search":
    query = st.text_input(
        "Enter an arXiv paper ID",
        placeholder="1706.03762"
    )

else:
    query = st.text_input(
        "Enter a research topic",
        placeholder="Retrieval Augmented Generation"
    )


# ---------------- SEARCH ----------------

if st.button("🔍 Search", type="primary"):

    if not query.strip():
        st.warning("Please enter a search query.")

    else:
        try:
            with st.spinner("Searching and generating your answer..."):

                # WIKIPEDIA AGENT
                if option == "Wikipedia Search":

                    agent = create_research_agent(
                        [machine_learning_search]
                    )

                    result = agent.invoke({
                        "messages": [
                            {
                                "role": "user",
                                "content": (
                                    f"Search Wikipedia for '{query}'. "
                                    "Explain the results with headings, "
                                    "examples, and source links."
                                )
                            }
                        ]
                    })

                    messages = result.get("messages", [])

                    st.subheader("📚 AI-Generated Answer")

                    if messages:
                        answer = messages[-1].content

                        if isinstance(answer, str):
                            st.markdown(answer)
                        elif isinstance(answer, list):
                            for block in answer:
                                if isinstance(block, dict):
                                    if block.get("type") == "text":
                                        st.markdown(block["text"])

                    tool_messages = [
                        m for m in messages
                        if getattr(m, "type", "") == "tool"
                    ]

                    if tool_messages:
                        with st.expander("🔧 Agent Execution Details"):
                            for message in tool_messages:
                                st.markdown(
                                    f"**Tool:** `{getattr(message, 'name', 'Tool')}`"
                                )
                                st.write(message.content)

                # ARXIV ID AND TOPIC SEARCH
                else:

                    raw_result = arxiv_paper_search.invoke({
                        "query": query
                    })

                    st.subheader("📄 arXiv Search Results")
                    st.markdown(raw_result)

                    if raw_result.startswith(
                        ("arXiv is temporarily unavailable",
                         "arXiv returned invalid XML",
                         "Could not retrieve")
                    ):
                        st.warning(
                            "The arXiv API did not return usable results."
                        )

                    elif raw_result != "No arXiv papers found for this query.":

                        with st.spinner("Generating AI explanation..."):

                            answer = llm.invoke(
                                "Explain these arXiv research results clearly. "
                                "Preserve paper titles, IDs, authors, URLs, "
                                "and abstract details. Do not invent facts.\n\n"
                                + raw_result
                            )

                        st.subheader("🤖 AI Explanation")
                        st.markdown(answer.content)

        except Exception as e:
            st.error(f"Search failed: {type(e).__name__}: {e}")

# ---------------- FOOTER ----------------

st.divider()
st.caption(
    "AI Research Assistant | Streamlit + LangChain + Groq + Wikipedia + arXiv"
)