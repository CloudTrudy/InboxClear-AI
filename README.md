# InboxClear AI
### Controlled, safety-conscious email triage using Strands Decider 2B and Amazon Bedrock

InboxClear AI is an AI-powered Gmail triage demonstration built for the **Agent Experience Hackathon: Strands Decider**. It explores how an AI agent can help people organise email while keeping the user in control of which messages are considered and what happens to them.

Rather than automatically processing an entire inbox, InboxClear AI uses a dedicated Gmail label to define a controlled batch of messages for the agent to assess. This makes the workflow easier to test, demonstrate, and review without treating every email in a user's inbox as eligible for automated action.

## The problem

Email inboxes can become difficult to manage when important messages, unwanted mail, and messages requiring further attention are mixed together. Automatically sorting messages also carries risks: a genuine opportunity, important request, or sensitive email could be incorrectly classified as junk.

InboxClear AI explores a more cautious approach: use an AI agent to help classify a selected group of emails, apply clear decision categories, and preserve a route for human review when a message should not be automatically dismissed.

## Why Gmail labels matter

The Gmail label **`InboxClear AI Demo`** defines the messages selected for the demonstration.

The user first applies this label to a chosen set of test emails. InboxClear AI then reads the messages carrying that label, rather than treating the entire inbox as its processing queue.

This design has several purposes:

- **User-controlled scope:** the user chooses which messages enter the triage workflow.
- **Safer testing:** the demonstration can be run against a prepared batch of emails.
- **Clear separation:** the selected test batch is distinct from other inbox messages.
- **More predictable demonstrations:** the agent works on a known set of messages, making its decisions easier to inspect.

The label is a scope-control mechanism for this workflow, not a complete security boundary. Gmail permissions and credentials must still be protected appropriately.

## How the workflow works

1. **Select a batch:** the user labels chosen Gmail messages `InboxClear AI Demo`.
2. **Read the selected emails:** the application retrieves the labelled messages, up to the configured limit of 10.
3. **Assess each message:** the agent evaluates the email and produces a triage classification.
4. **Apply safety checks:** a separate Amazon Bedrock-powered check helps identify messages that may be unsafe to dismiss or whose classification warrants caution.
5. **Handle the result:** the application uses the triage category to determine the appropriate action.
6. **Keep uncertainty visible:** messages requiring further attention can remain available for human review instead of being automatically archived.

## Triage categories

| Category | Intended behaviour |
| --- | --- |
| **IMPORTANT** | Keep the message in the inbox. |
| **JUNK** | Apply the junk label and archive the message; do not delete it. |
| **REVIEW** | Leave the message unchanged for a person to assess. |

The distinction between **JUNK** and **REVIEW** is intentional. An uncertain classification should not automatically become an archive action. The goal is to assist with triage while reducing the risk of hiding a message that deserves attention.

## Safety-first design

InboxClear AI is designed as a demonstration of controlled automation rather than unrestricted inbox management.

- Only messages selected with the dedicated demo label are in scope.
- The number of messages processed is limited for the demonstration.
- A safety check helps challenge potentially harmful or inappropriate junk classifications.
- Messages classified as junk are archived, not permanently deleted.
- Messages marked for review are left unchanged so a person can make the final judgement.

AI classification is not infallible. Users should inspect the results and verify any actions before relying on the system for important email.

## Technology

- Python
- Streamlit
- Gmail API
- Amazon Bedrock
- Strands Decider 2B

## Reusable decision pattern: Confidence-gated email triage

**Pattern type:** Policy and guardrails  
**Decision question:** `email_triage`  
**Decision type:** `choice`  
**Options:** `IMPORTANT`, `JUNK`, `REVIEW`

InboxClear AI uses Strands Decider 2B through the Strands Decider System One endpoint. For each email, the application sends the sender, subject, and email body as context, along with a typed `email_triage` question. The question defines three explicit choices and provides criteria to guide the decision.

Email content is treated as untrusted data, never as instructions. The application validates the returned category and applies a confidence threshold of `0.60` in its classification flow. Protective rules help preserve certain important messages, while a separate Amazon Bedrock safety check evaluates proposed junk classifications before the application can archive them.

If the safety check identifies a potentially important message, returns an unexpected result, or fails, the application uses the safer REVIEW outcome rather than automatically archiving the email. Messages classified as REVIEW are left unchanged. Messages classified as JUNK are labelled and archived, not deleted.

### How to reuse this pattern

1. Define a typed choice question with explicit, permitted outcomes.
2. Provide clear criteria for each choice, including when to select REVIEW.
3. Send relevant context to the Decider endpoint.
4. Validate the returned choice and apply an appropriate confidence policy.
5. Add safety checks before allowing decisions to trigger consequential actions.
6. Fail safely when a decision is invalid, uncertain, or a safety check cannot complete.

This pattern can be adapted for support-ticket routing, document classification, or task prioritisation by changing the question, options, criteria, and safety checks to suit the new use case.

**Hackathon pattern declaration:** Policy and guardrails.

**Tags:** `#strands-decider-2b` `#policy` `#guardrails`

## Running locally

InboxClear AI requires Python, Gmail API access, AWS credentials, and permission to invoke the configured Amazon Bedrock model. The Streamlit application communicates with a separately running Strands Decider System One service at `http://127.0.0.1:8099/v1/systemone`.

The application is configured to run locally on port `8505`. The Decider service must be available on port `8099` for email classification to work. Follow the final repository setup instructions to install dependencies and start both services.

Gmail access requires an authorised OAuth setup. Amazon Bedrock access requires valid AWS credentials and model permissions in the configured AWS region.

**Security note:** Never commit Gmail credentials, access tokens, AWS secrets, or other private configuration files to the repository.

## Limitations

InboxClear AI is a hackathon demonstration, not a guarantee of correct email classification or a replacement for human judgement. AI decisions can be wrong, and confidence scores do not guarantee correctness.

The `InboxClear AI Demo` Gmail label limits which messages the application selects for processing, but it is not a complete security boundary. Review decisions carefully before applying them, and do not rely on this demonstration as the sole safeguard for important email.

## Author

**Trudy-Ann Foster**

Built for the **Agent Experience Hackathon: Strands Decider**, October 2026.