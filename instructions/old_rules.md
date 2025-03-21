# General Coding Principles for AI Assistant

**Write Clean, Simple, and Readable Code:** Prioritize code clarity and simplicity above all else. The code should be easy to understand, maintain, and debug by any developer. - Aim for code that is self-explanatory through clear structure, naming, and comments. - Avoid over-engineering or unnecessary complexity.

**Implement Features in the Simplest Possible Way:** Choose the most straightforward and efficient approach to implement each feature. - Start with the simplest solution that meets the requirements. - Avoid premature optimization or adding complexity before it is needed.

**Keep Files Small and Focused:** Structure code into small, modular files, each responsible for a specific set of functionalities. - Aim for files that are easy to navigate and understand at a glance (consider a guideline of <200 lines, but adapt based on complexity). - Promote modularity and separation of concerns by breaking down large functionalities into smaller, focused modules.

**Test After Every Meaningful Change:** Adopt a test-driven or test-integrated development approach. Write tests to verify the correctness of code changes frequently. - Write unit tests, integration tests, or other relevant tests to ensure each component and feature works as expected. - Testing should be an integral part of the development process, not an afterthought.

**Focus on Core Functionality Before Optimization:** Prioritize implementing the core functionality of a feature correctly and completely before focusing on performance optimization. - Ensure the feature works as intended first. - Optimize for performance only after the core functionality is implemented and tested, and if performance bottlenecks are identified.

**Use Clear and Consistent Naming:** Employ clear, descriptive, and consistent naming conventions for variables, functions, classes, modules, and files. - Choose names that accurately reflect the purpose and functionality of the code elements. - Follow established naming conventions for the target programming language and project. - Consistency in naming improves code readability and reduces cognitive load.

**Think Thoroughly Before Coding (Plan and Reason):** Before writing code, take time to think through the problem, plan the solution, and reason about the approach. - Understand the requirements and constraints clearly. - Outline the steps or logic needed to solve the problem. - Consider different approaches and choose the most appropriate one. - Briefly explain the reasoning behind the chosen approach (e.g., in comments or a short descriptive paragraph).

**Always Write Simple, Clean, and Modular Code:** Reinforce the principles of simplicity, clarity, and modularity as the guiding principles for all code generation. - Strive for code that is easy to understand, modify, and reuse. - Favor modular design to break down complex systems into manageable, independent components.

**Use Clear and Easy-to-Understand Language in Communication:** When communicating with the user (explanations, instructions, questions), use clear, concise, and easy-to-understand language. - Write in short, direct sentences. - Avoid jargon or overly technical terms unless necessary and explained. - Focus on clarity and effective communication.

## Error Resolution Strategy for AI Assistant

- **DO NOT JUMP TO CONCLUSIONS! Consider Multiple Possible Causes:** When encountering an error, resist the urge to immediately assume a single cause.

  - Systematically consider multiple potential reasons for the error before deciding on a fix.
  - Explore different possibilities and rule them out methodically.

- **Explain the Problem in Plain English:** Before attempting to fix an error, articulate the problem clearly and concisely in plain English.

  - Describe the observed error, the expected behavior, and the discrepancy between them.
  - This step helps to clarify understanding and guide the debugging process.

- **Make Minimal Necessary Changes (Principle of Least Change):** When fixing an error, aim to make the minimum changes required to resolve the issue.

  - Change as few lines of code as possible to fix the problem effectively.
  - Avoid making sweeping or unnecessary changes that could introduce new issues.
  - Focus on targeted fixes that address the specific error.

- **In Case of Unclear or Strange Errors, Utilize Web Search (and Suggest to User):** When faced with errors that are difficult to understand or resolve, leverage web search engines to find relevant information and solutions.
  - If the AI is unable to resolve a strange or unclear error independently, suggest to the user to perform a web search using relevant keywords (e.g., error message, technology, problem description).
  - Web search can provide access to up-to-date documentation, forums, and community knowledge that can be helpful for troubleshooting.

### Building and Testing Process for AI Assistant

- **Verify Each New Feature Works (Provide Testing Instructions):** After implementing a new feature or functionality, ensure it works correctly by verifying its behavior and functionality.

  - For each new feature, explicitly describe to the user how to test and verify that the feature is working as expected.
  - Provide clear and actionable testing steps or commands that the user can follow.

- **DO NOT Write Complicated and Confusing Code. Opt for Simple & Modular Approach (Reiteration):** Re-emphasize the preference for simplicity and modularity in the coding process.

  - Avoid generating overly complex or convoluted code that is difficult to understand and test.
  - Consistently choose simple and modular solutions whenever possible.

- **When Not Sure What to Do, Utilize Web Search (and Suggest to User):** When faced with uncertainty about the best approach to implement a feature or resolve a problem, use web search to explore options and gather information.
  - If the AI is unsure how to proceed, suggest to the user to perform a web search for relevant techniques, libraries, or examples.
  - Web search can help in exploring different solutions and making informed decisions.

### Code Comments - Importance and Usage (Integrated Section)

- **Mandatory Code Commenting (Emphasis on Clarity):** **Always add comments to the generated code.** Code comments are **essential** for code readability, maintainability, and understanding the logic. Comments serve as documentation within the code itself and are crucial for collaboration, debugging, and future modifications.

- **Rationale for Comments:**

  - **Improved Readability:** Comments explain the _intent_ and _purpose_ of code, making it easier to understand.
  - **Enhanced Maintainability:** Well-commented code is significantly easier to maintain, modify, and debug over time.
  - **Documentation within Code:** Comments act as inline documentation, providing context and explanations directly where needed.
  - **Collaboration Facilitation:** Comments are vital for team collaboration.

- **When to Add Comments (Prioritize Clarity in Complex Areas):** Add comments liberally, especially for:

  - **Complex Logic:** Algorithms, intricate business logic, non-trivial control flow. Explain steps, reasoning.
  - **Non-Obvious Code:** Clarify intent and behavior of code that might not be immediately understood.
  - **API Interactions:** Purpose, data formats, expected responses, error handling for external API, database, library interactions.
  - **Design Decisions & Rationale:** Explain significant design choices and architectural patterns.
  - **Tricky/Edge Cases:** Document handling of edge cases, unusual inputs, potential pitfalls.
  - **Configuration & Setup:** Explain purpose of settings and parameters in configuration code.
  - **Functions & Methods:** Use docstrings to explain purpose, parameters, return values, exceptions.

**What to Comment (Focus on Intent and Context):** Focus comments on: - **Purpose:** Goal of the code section/function, problem solved. - **Logic:** Briefly describe algorithm/approach, explain steps. - **Assumptions:** Document assumptions (input types, data formats, preconditions). - **Limitations:** Note limitations, unhandled edge cases, areas for improvement. - **Usage:** For functions/methods, explain how to use, parameters, expected results.

**Discouraging Comment Removal (Preserve Documentation):** **Do not delete comments unless absolutely necessary.** Comments are valuable documentation and should be preserved. Before removal, consider:

**Redundancy:** Is the comment truly redundant and adding no value? Context is often not obvious from code alone.
**Readability/Maintainability:** Will removing reduce readability or maintainability? Err on caution and keep comments.
**Update vs. Delete:** If outdated/incorrect, update the comment, don't delete it.
**Types of Comments (Language Specific):** Use appropriate comment types for the target language (e.g., docstrings, inline comments in Python; JSDoc in JavaScript etc.).
