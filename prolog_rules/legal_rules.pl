% Domain-specific rules for the "Legal" domain
% Now includes human-readable mappings (Controlled Natural Language - CNL)

% --- Main Entry Point ---

legal_rules(Statement, IntentData) :-
    play_language_game(
        Statement,
        game_data{
            type: "legal_query",
            intent_data: IntentData,
            parsing_logic: parse_legal_query,
            validation_logic: validate_legal_query,
            action_logic: handle_legal_request
        }
    ).

% --- Handling Legal Queries ---

% Handles questions about legal definitions and precedents.
handle_legal_request(ParsedQuery) :-
    ParsedQuery = query{topic: Topic, intent: Intent},
    legal_topic(Topic),
    execute_legal_intent(Intent, Topic).

% --- Query Parsing and Validation ---

% Parses legal queries to extract topic and intent.
parse_legal_query(Statement, ParsedQuery) :-
    play_language_game(
        Statement,
        game_data{
            type: "parse_query",
            parsing_logic: extract_legal_topic_and_intent,
            result_var: ParsedQuery
        }
    ).

% Validates the legal query for scope and accuracy.
validate_legal_query(ParsedQuery) :-
    play_language_game(
        ParsedQuery,
        game_data{
            type: "validate_query",
            validation_logic: ensure_legal_relevance_and_accuracy
        }
    ).

% --- Legal Actions ---

% Executes actions based on intent and legal topic.
execute_legal_intent(ask_question, Topic) :-
    format("Here is a detailed explanation about ~w based on legal precedent.", [Topic]).

execute_legal_intent(get_information, Topic) :-
    format("Here is relevant legal information about ~w.", [Topic]).

% --- Helper Logic ---

% Extracts topic and intent from a legal query.
extract_legal_topic_and_intent(Statement, query{topic: Topic, intent: Intent}) :-
    % Simulated logic for parsing (replace with advanced methods if needed).
    member(Topic, ["contract law", "intellectual property", "criminal law", "civil rights"]),
    member(Intent, ["ask_question", "get_information"]).

% Validates the query for relevance and accuracy in the legal domain.
ensure_legal_relevance_and_accuracy(Query) :-
    Query = query{topic: Topic},
    legal_topic(Topic).

% Checks if the topic is valid in the legal domain.
legal_topic(Topic) :-
    member(Topic, ["contract law", "intellectual property", "criminal law", "civil rights", "legislation"]).

% --- Controlled Natural Language (CNL) Mappings ---

% Converts a human-readable statement into a Prolog rule.
cnl_to_prolog("A contract is a legally binding agreement between two or more parties.", contract(X, Y) :- legally_binding_agreement(X, Y)).
cnl_to_prolog("Intellectual property refers to creations of the mind such as inventions, literary works, and artistic designs.", intellectual_property(X) :- creation_of_mind(X)).
cnl_to_prolog("A crime is an action that violates a law and is punishable by the state.", crime(X) :- violates_law(X), punishable_by_state(X)).
cnl_to_prolog("Civil rights protect individuals from discrimination and guarantee equal treatment under the law.", civil_rights(X) :- protects_individuals(X), guarantees_equality(X)).

% Converts a Prolog rule into a human-readable statement.
prolog_to_cnl(contract(X, Y) :- legally_binding_agreement(X, Y), "A contract is a legally binding agreement between two or more parties.").
prolog_to_cnl(intellectual_property(X) :- creation_of_mind(X), "Intellectual property refers to creations of the mind such as inventions, literary works, and artistic designs.").
prolog_to_cnl(crime(X) :- violates_law(X), punishable_by_state(X), "A crime is an action that violates a law and is punishable by the state.").
prolog_to_cnl(civil_rights(X) :- protects_individuals(X), guarantees_equality(X), "Civil rights protect individuals from discrimination and guarantee equal treatment under the law.").

% --- Example Usage ---

% legal_rules("What is the legal definition of negligence?", intent_data{primary_intent: get_information}).
% legal_rules("Can I sue someone for breach of contract?", intent_data{primary_intent: ask_question}).
% legal_rules("What are my civil rights regarding free speech?", intent_data{primary_intent: get_information}).
