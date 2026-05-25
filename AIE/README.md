# Glossary

Here is the glossary of special terms, defining them within the context of building production-ready AI agent systems:

## **A**

* **Agent Engineering**
The practice of building complex, multi-component software systems where an LLM orchestrates decisions, coordinates tools, and executes real-world tasks. It shifts the focus from writing text instructions to designing resilient software architectures.


* **API (Application Programming Interface) Call**
A request made by the AI agent to an external service or software application to retrieve data or execute an action (e.g., booking a flight or querying a database).


* **Attack Surface**
The sum total of all points or vulnerabilities in a system where an unauthorized user (or malicious input) can try to enter data, manipulate the system, or extract unauthorized information.



## **C**

* **Circuit Breaker**
A design pattern in reliability engineering used to detect systemic failures and encapsulate the logic of preventing a failure from cascading and bringing down the entire system.


* **Context**
The temporary workspace or information window fed into an LLM during a request, which the model uses to understand the user's intent and formulate its response.


* **Contract**
A strict agreement or schema between an AI agent and a tool that explicitly defines what inputs the tool requires and what outputs it will return.



## **E**

* **Embedding Model**
A machine learning model that converts text into mathematical vectors (numerical representations) so the system can measure how close or similar different concepts are in meaning.


* **Evaluation Pipelines**
Automated testing frameworks containing test cases with known good answers used to measure concrete system metrics before shipping code to production.



## **F**

* **Fallback Paths**
Pre-designed "Plan B" alternative routes or operations that an agent system switches to automatically when its primary plan or tool call fails.



## **I**

* **Input Validation**
A security practice that inspects and cleanses data or user inputs before they reach the LLM, specifically designed to catch malicious, malformed, or unauthorized requests.



## **L**

* **Latency**
The amount of time it takes for the AI agent system to process a request and return a response or complete a task.



## **O**

* **Output Filters**
Security mechanisms that check the agent’s generated responses before they are sent to the user, blocking any outputs that violate safety or organizational policies.



## **P**

* **Permission Boundaries**
Security limits imposed on an AI agent that strictly control what it is authorized to attempt, such as limiting write access to databases or requiring human approval before sending emails.


* **Product Thinking**
A non-technical discipline focused on user experience (UX) and human psychology, ensuring an unpredictable system is designed to handle errors gracefully and build human trust.


* **Prompt Engineering**
The practice of crafting, formatting, and refining clever text instructions for a standalone language model to get a desired textual response.


* **Prompt Injections**
A security exploit where a user embeds malicious instructions within their input to override or bypass the agent's core system prompts and safety rules.



## **R**

* **RAG (Retrieval-Augmented Generation)**
An architectural approach where an agent fetches relevant documents from an external dataset and appends them to the LLM's context window, allowing it to answer questions using specific, up-to-date data rather than just its training memory.


* **Regressions**
Bugs or unintended performance drops where a system's existing functionality breaks after a new update or change is introduced.


* **Re-ranking**
A secondary pass in the retrieval process that scores initially fetched documents by actual relevance, pushing the highest-quality data to the top of the context pile.


* **Retry Logic with Back-off**
A reliability mechanism where a system automatically retries a failed API request, but spaces out the time between attempts so it does not overwhelm or "hammer" a struggling external service.



## **S**

* **Schema**
A structured, explicit blueprint or data format that defines the strict types, patterns, and required variables for a tool's inputs and outputs.


* **System Design**
The process of defining the architecture, components, modules, interfaces, and data flow for a system to satisfy specified requirements.



## **T**

* **Timeouts**
A specified period of time after which a system will stop waiting for an unhelpful or non-responsive external API, preventing the agent from hanging indefinitely.


* **Tracing**
The continuous practice of logging every single step, decision, tool call, parameter, and internal reasoning path an agent takes so that errors can be diagnosed with data rather than guesswork.


---

# The 7 Core Skills of an Agent Engineer

## 1. System Design

* 
**The Essence:** Moving away from a single model and treating an agentic system like an orchestra.


* **Key Focus:** Designing the architecture of data flow and coordination between LLMs, tools, databases, and sub-agents so they function structurally without failing.



## 2. Tool & Contract Design

* **The Essence:** Ensuring the tools your agent interacts with have strict, unambiguous guidelines.


* **Key Focus:** Writing explicit schemas with strict types, patterns, and examples. Without tight constraints, an LLM will use its "imagination" to fill in the gaps, leading to unpredictable behavior.



## 3. Retrieval Engineering (RAG)

* **The Essence:** Ensuring the context fed into your model is highly relevant signal, not random noise.


* **Key Focus:** Perfecting document chunking strategies, optimizing how embedding models represent meaning, and utilizing re-ranking pipelines to prioritize the most relevant data.



## 4. Reliability Engineering

* **The Essence:** Standard software and external APIs fail; your agent must be built to handle those failures gracefully.


* **Key Focus:** Implementing classic backend engineering practices such as retry logic with back-offs, timeouts, fallback paths (Plan B options), and circuit breakers to prevent cascading system failures.



## 5. Security & Safety

* **The Essence:** Protecting your agent from being manipulated or weaponized against you.


* **Key Focus:** Defending against prompt injections via input validation, setting up output filters to block policy-violating responses, and strictly limiting the agent's permission boundaries (e.g., restricting direct database write access or unapproved emailing).



## 6. Evaluation & Observability

* **The Essence:** Replacing "vibes" and guesswork with definitive data and metrics.


* **Key Focus:** Setting up tracing pipelines to log every decision, tool call, and reasoning step. You must establish evaluation pipelines with known test cases to measure concrete metrics like success rate, latency, and cost per task.



## 7. Product Thinking & UX

* **The Essence:** Designing an experience for a system that is inherently unpredictable.


* **Key Focus:** Building human trust by ensuring the agent handles errors gracefully, clearly signals when it is certain vs. uncertain, and knows exactly when to ask a human for clarification or escalate the task entirely.



---

## Where to Start: High-Leverage Actions

If you want to transition from prompt engineering to agent engineering, you don't need to go back to school. Do these two things first:

1. **Tighten Your Tool Schemas:** Read your tool schemas out loud. If a new engineer wouldn't immediately understand the exact expected input and output, fix it by adding strict types and precise examples.


2. **Trace a Single Failure Backward:** Instead of trying to fix a bug by rewriting your prompt text, trace the system logs. Look at whether the correct tool was selected, if the right document was retrieved, or if the schema was vague.



> 
> **The Takeaway:** Nine times out of ten, a production AI agent fails because of a system flaw, not because of the words in the prompt. Fix the system, not just the sentences.
> 
>
