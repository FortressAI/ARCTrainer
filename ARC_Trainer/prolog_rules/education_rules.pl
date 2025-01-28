% education_rules.pl
% Domain-specific rules for the "Education" domain

% --- Debugging & Configuration ---
:- discontiguous cnl_to_prolog/3.
:- discontiguous cnl_to_prolog/4.
:- discontiguous prolog_to_cnl/3.
:- discontiguous prolog_to_cnl/4.
:- multifile cnl_to_prolog/3.
:- multifile prolog_to_cnl/3.

% --- Main Entry Point ---

education_rules(Response, IntentData) :-
    play_language_game(
        Response,
        game_data{
            type: "education_query",
            intent_data: IntentData,
            parsing_logic: parse_educational_query,
            validation_logic: validate_educational_query,
            action_logic: handle_education_request
        }
    ).

% --- Handling Educational Queries ---

% Handles a request for academic guidance.
handle_ask_question(Response) :-
    play_language_game(
        Response,
        game_data{
            type: "ask_question",
            intent_data: intent_data{primary_intent: ask_question},
            action_logic: provide_academic_guidance
        }
    ).

% Handles a request for educational resources.
handle_get_information(Response) :-
    play_language_game(
        Response,
        game_data{
            type: "get_information",
            intent_data: intent_data{primary_intent: get_information},
            action_logic: provide_educational_resources
        }
    ).

% --- Query Parsing and Validation ---

% Parses the educational query to extract its intent and subject.
parse_educational_query(Response, ParsedQuery) :-
    play_language_game(
        Response,
        game_data{
            type: "parse_query",
            parsing_logic: extract_subject_and_intent,
            result_var: ParsedQuery
        }
    ).

% Validates the parsed query for relevance and accuracy.
validate_educational_query(ParsedQuery) :-
    play_language_game(
        ParsedQuery,
        game_data{
            type: "validate_query",
            validation_logic: check_relevance_and_accuracy
        }
    ).

% --- Educational Actions ---

% Provides academic guidance based on the parsed query.
provide_academic_guidance(ParsedQuery) :-
    ParsedQuery = query{subject: Subject},
    educational_subject(Subject),
    format("Here is some guidance for your question about ~w.", [Subject]).

% Provides resources for educational purposes.
provide_educational_resources(ParsedQuery) :-
    ParsedQuery = query{subject: Subject},
    educational_subject(Subject),
    format("Here are recommended resources for studying ~w.", [Subject]).

% --- Helper Logic ---

% Extracts subject and intent from a query using language games.
extract_subject_and_intent(Response, query{subject: Subject, intent: Intent}) :-
    % Simulated logic for subject and intent extraction.
    % Replace with actual parsing methods or LLM integration.
    member(Subject, ["math", "science", "history", "literature"]),
    member(Intent, ["ask_question", "get_information"]).

% Validates the query's relevance and accuracy.
check_relevance_and_accuracy(Query) :-
    Query = query{subject: Subject},
    educational_subject(Subject).

% Checks if the subject is part of the educational domain.
educational_subject(Subject) :-
    member(Subject, ["math", "science", "history", "literature", "research", "study"]).

% --- Controlled Natural Language (CNL) Mappings ---

% Converts a human-readable statement into a Prolog rule.
cnl_to_prolog("A teacher provides knowledge and guidance to students.", 
              teacher(X) :- provides_knowledge(X), guides_students(X)).

cnl_to_prolog("Mathematics is a subject that involves numbers, logic, and problem-solving.", 
              subject(math) :- involves(numbers), involves(logic), involves(problem_solving)).

cnl_to_prolog("History is the study of past events and civilizations.", 
              subject(history) :- studies(past_events), studies(civilizations)).

cnl_to_prolog("Literature includes written works such as poetry, novels, and plays.", 
              subject(literature) :- includes(poetry), includes(novels), includes(plays)).

% Converts a Prolog rule into a human-readable statement.
prolog_to_cnl(teacher(X) :- provides_knowledge(X), guides_students(X), 
              "A teacher provides knowledge and guidance to students.").

prolog_to_cnl(subject(math) :- involves(numbers), involves(logic), involves(problem_solving), 
              "Mathematics is a subject that involves numbers, logic, and problem-solving.").

prolog_to_cnl(subject(history) :- studies(past_events), studies(civilizations), 
              "History is the study of past events and civilizations.").

prolog_to_cnl(subject(literature) :- includes(poetry), includes(novels), includes(plays), 
              "Literature includes written works such as poetry, novels, and plays.").

% --- Example Usage ---

% education_rules("What is the Pythagorean theorem?", intent_data{primary_intent: get_information}).
% education_rules("Can you help me with my science homework?", intent_data{primary_intent: ask_question}).
% education_rules("Where can I find research papers on climate change?", intent_data{primary_intent: get_information}).
