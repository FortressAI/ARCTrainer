% healthcare_rules.pl
% Domain-specific rules for the "Healthcare" domain
% Now includes human-readable mappings (Controlled Natural Language - CNL)

% --- Debugging & Configuration ---
:- discontiguous cnl_to_prolog/3.
:- discontiguous cnl_to_prolog/4.
:- discontiguous prolog_to_cnl/3.
:- discontiguous prolog_to_cnl/4.
:- multifile cnl_to_prolog/3.
:- multifile prolog_to_cnl/3.

% --- Main Entry Point ---

healthcare_rules(Statement, IntentData) :-
    play_language_game(
        Statement,
        game_data{
            type: "healthcare_query",
            intent_data: IntentData,
            parsing_logic: parse_healthcare_query,
            validation_logic: validate_healthcare_query,
            action_logic: handle_healthcare_request
        }
    ).

% --- Handling Healthcare Queries ---

% Handles requests for general healthcare advice.
handle_healthcare_request(ParsedQuery) :-
    ParsedQuery = query{topic: Topic, intent: Intent},
    healthcare_topic(Topic),
    execute_healthcare_intent(Intent, Topic).

% --- Query Parsing and Validation ---

% Parses healthcare queries to extract intent and topic.
parse_healthcare_query(Statement, ParsedQuery) :-
    play_language_game(
        Statement,
        game_data{
            type: "parse_query",
            parsing_logic: extract_healthcare_intent_and_topic,
            result_var: ParsedQuery
        }
    ).

% Validates the healthcare query for ethical relevance.
validate_healthcare_query(ParsedQuery) :-
    play_language_game(
        ParsedQuery,
        game_data{
            type: "validate_query",
            validation_logic: ensure_healthcare_ethics
        }
    ).

% --- Healthcare Actions ---

% Executes the appropriate action based on intent and topic.
execute_healthcare_intent(seek_advice, Topic) :-
    format("For general advice on ~w, please consult a healthcare professional.", [Topic]).

execute_healthcare_intent(get_information, Topic) :-
    format("Here is general information about ~w. Note: This is not a substitute for medical advice.", [Topic]).

% --- Learning System for Healthcare Queries ---
% Allows Prolog to store and recall previously answered healthcare queries.

learn_healthcare_query(Question, Answer) :-
    assertz(stored_healthcare_query(Question, Answer)),
    format("Healthcare query stored: ~w -> ~w.", [Question, Answer]).

recall_healthcare_query(Question, Answer) :-
    stored_healthcare_query(Question, Answer),
    format("Previously answered: ~w -> ~w.", [Question, Answer]).

% --- Helper Logic ---

% Extracts intent and topic from a healthcare query.
extract_healthcare_intent_and_topic(Statement, query{topic: Topic, intent: Intent}) :-
    % Simulated logic for parsing (replace with advanced methods if needed).
    member(Topic, ["symptoms", "treatment", "diseases", "nutrition", "exercise"]),
    member(Intent, ["seek_advice", "get_information"]).

% Ensures the query is ethical and adheres to healthcare guidelines.
ensure_healthcare_ethics(Query) :-
    Query = query{topic: Topic},
    healthcare_topic(Topic).

% Checks if the topic is valid in the healthcare domain.
healthcare_topic(Topic) :-
    member(Topic, ["symptoms", "treatment", "diseases", "nutrition", "exercise"]).

% --- Controlled Natural Language (CNL) Mappings ---

% Converts a human-readable statement into a Prolog rule.
cnl_to_prolog("Symptoms are the observable effects of a disease.", 
              symptom(X) :- disease(Y), causes(Y, X)).
cnl_to_prolog("A treatment is a medical intervention aimed at curing or managing a disease.", 
              treatment(T) :- disease(D), manages(T, D)).
cnl_to_prolog("A balanced diet is essential for maintaining good health.", 
              balanced_diet(healthy)).
cnl_to_prolog("Regular exercise helps prevent many chronic conditions.", 
              exercise(prevent_chronic_conditions)).

% Converts a Prolog rule into a human-readable statement.
prolog_to_cnl(symptom(X) :- disease(Y), causes(Y, X), 
              "Symptoms are the observable effects of a disease.").
prolog_to_cnl(treatment(T) :- disease(D), manages(T, D), 
              "A treatment is a medical intervention aimed at curing or managing a disease.").
prolog_to_cnl(balanced_diet(healthy), 
              "A balanced diet is essential for maintaining good health.").
prolog_to_cnl(exercise(prevent_chronic_conditions), 
              "Regular exercise helps prevent many chronic conditions.").

% --- Example Usage ---

% learn_healthcare_query("What are the symptoms of the flu?", "Common symptoms include fever, cough, and fatigue.").
% recall_healthcare_query("What are the symptoms of the flu?", Answer). -> Previously answered: Flu symptoms -> fever, cough, fatigue.
% healthcare_rules("Can I share patient information with their family?", intent_data{primary_intent: seek_advice}).
% healthcare_rules("What is the best exercise for weight loss?", intent_data{primary_intent: get_information}).
