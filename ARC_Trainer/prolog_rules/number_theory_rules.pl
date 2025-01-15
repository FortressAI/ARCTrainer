% Domain-specific rules for IMO Number Theory problems

% --- Core Number-Theoretic Principles ---

% Determines if a number is prime.
prime(2).
prime(3).
prime(P) :-
    P > 3,
    P mod 2 =\= 0,
    \+ has_divisor(P, 3).

has_divisor(N, I) :-
    N mod I =:= 0.
has_divisor(N, I) :-
    I * I < N,
    I2 is I + 2,
    has_divisor(N, I2).

% Computes the greatest common divisor (GCD) using the Euclidean algorithm.
gcd(X, 0, X) :- X > 0.
gcd(X, Y, Gcd) :-
    Y > 0,
    R is X mod Y,
    gcd(Y, R, Gcd).

% Computes the least common multiple (LCM).
lcm(X, Y, Lcm) :-
    gcd(X, Y, Gcd),
    Lcm is X * Y // Gcd.

% --- Main Entry Point ---

number_theory_rules(Statement, IntentData) :-
    play_language_game(
        Statement,
        game_data{
            type: "number_theory_query",
            intent_data: IntentData,
            parsing_logic: parse_number_theory_query,
            validation_logic: validate_number_theory_query,
            action_logic: handle_number_theory_request
        }
    ).

% --- Handling Number Theory Queries ---

% Handles queries about number properties and operations.
handle_number_theory_request(ParsedQuery) :-
    ParsedQuery = query{property: Property, number: Number},
    execute_number_theory_action(Property, Number).

% --- Query Parsing and Validation ---

% Parses a number theory query to extract the number and property.
parse_number_theory_query(Statement, ParsedQuery) :-
    play_language_game(
        Statement,
        game_data{
            type: "parse_query",
            parsing_logic: extract_number_and_property,
            result_var: ParsedQuery
        }
    ).

% Validates the parsed query for correctness.
validate_number_theory_query(ParsedQuery) :-
    play_language_game(
        ParsedQuery,
        game_data{
            type: "validate_query",
            validation_logic: check_number_theory_relevance
        }
    ).

% --- Number Theory Actions ---

% Executes actions based on number theory properties.
execute_number_theory_action("prime", Number) :-
    (prime(Number) -> format("~w is a prime number.", [Number]) ; format("~w is not a prime number.", [Number])).

execute_number_theory_action("gcd", Data) :-
    Data = [X, Y],
    gcd(X, Y, Gcd),
    format("The greatest common divisor of ~w and ~w is ~w.", [X, Y, Gcd]).

execute_number_theory_action("lcm", Data) :-
    Data = [X, Y],
    lcm(X, Y, Lcm),
    format("The least common multiple of ~w and ~w is ~w.", [X, Y, Lcm]).

% --- Helper Logic ---

% Extracts the number and property from a query.
extract_number_and_property(Statement, query{property: Property, number: Number}) :-
    % Simulated logic for parsing (replace with advanced methods if needed).
    member(Property, ["prime", "gcd", "lcm"]),
    extract_numbers_from_statement(Statement, Number).

% Extracts numbers from a statement.
extract_numbers_from_statement(Statement, Numbers) :-
    % Simulated logic to extract numbers from input.
    % Replace with actual number extraction methods or LLM-based parsing.
    atom_chars(Statement, Chars),
    findall(Number, (member(Char, Chars), atom_number(Char, Number)), Numbers).

% Checks if the query is relevant to number theory.
check_number_theory_relevance(Query) :-
    Query = query{property: Property},
    member(Property, ["prime", "gcd", "lcm"]).

% --- Example Usage ---

% number_theory_rules("Is 7 a prime number?", intent_data{primary_intent: ask_question}).
% number_theory_rules("What is the gcd of 54 and 24?", intent_data{primary_intent: get_information}).
% number_theory_rules("Find the lcm of 12 and 15.", intent_data{primary_intent: ask_question}).
