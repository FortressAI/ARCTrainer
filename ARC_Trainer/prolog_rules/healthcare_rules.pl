% Domain-specific rules for the "Healthcare" domain

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

% --- Example Usage ---

% healthcare_rules("What are the symptoms of the flu?", intent_data{primary_intent: get_information}).
% healthcare_rules("Can I share patient information with their family?", intent_data{primary_intent: seek_advice}).
% healthcare_rules("What is the best exercise for weight loss?", intent_data{primary_intent: get_information}).
