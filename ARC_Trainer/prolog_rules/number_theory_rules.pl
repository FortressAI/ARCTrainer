% control_agent/prolog_logic/number_theory_rules.pl

% Domain-specific rules for IMO Number Theory problems

% --- Number Properties ---

prime(2).
prime(3).
prime(P) :-
    integer(P),
    P > 3,
    P mod 2 =\= 0,
    \+ has_divisor(P, 3).

has_divisor(N, I) :-
    0 =:= N mod I.
has_divisor(N, I) :-
    I * I < N,
    I2 is I + 2,
    has_divisor(N, I2).

divisible(X, Y) :-
    integer(X),
    integer(Y),
    Y \= 0,
    0 =:= X mod Y.

coprime(X, Y) :-
    integer(X),
    integer(Y),
    gcd(X, Y, 1).

% --- Greatest Common Divisor (GCD) ---

gcd(X, 0, X) :-
    X > 0.
gcd(X, Y, Gcd) :-
    Y > 0,
    Z is X mod Y,
    gcd(Y, Z, Gcd).

% --- Least Common Multiple (LCM) ---

lcm(X, Y, Lcm) :-
    integer(X),
    integer(Y),
    X > 0,
    Y > 0,
    gcd(X, Y, Gcd),
    Lcm is X * Y // Gcd.

% --- Modular Arithmetic ---

mod_inverse(A, M, Inverse) :-
    integer(A),
    integer(M),
    M > 1,
    coprime(A, M),
    find_mod_inverse(A, M, 1, Inverse).

find_mod_inverse(A, M, I, Inverse) :-
    0 =:= (A * I) mod M,
    Inverse is I.
find_mod_inverse(A, M, I, Inverse) :-
    I < M,
    I1 is I + 1,
    find_mod_inverse(A, M, I1, Inverse).

% --- Rules for specific number-theoretic functions ---

factorial(0, 1).
factorial(N, F) :-
    N > 0,
    N1 is N - 1,
    factorial(N1, F1),
    F is N * F1.

% --- Validation Rules ---

% Example: Validate a statement about prime numbers
validate_statement(Statement, IntentData) :-
    IntentData = intent_data{primary_intent: Intent},
    (Intent == solve_problem ; Intent == get_information ; Intent == ask_question),
    contains_keyword(Statement, ["prime", "number"]),
    validate_prime_statement(Statement).

validate_prime_statement(Statement) :-
    extract_number_from_statement(Statement, Number),
    ( prime(Number)
    -> \+ contains_keyword(Statement, ["not", "prime"])
    ; contains_keyword(Statement, ["not", "prime"])
    ).

% Example: Validate divisibility claims
validate_divisibility(Statement, IntentData) :-
    IntentData = intent_data{primary_intent: solve_problem},
    contains_keyword(Statement, ["divisible", "by"]),
    extract_numbers_from_statement(Statement, [Num1, Num2]),
    divisible(Num1, Num2).

% --- Utility Predicates ---

is_number(Term) :- % added from control_agent.pl as it is general
    number(Term).

is_number(Term) :-
    atom(Term),
    atom_number(Term, _).

extract_number_from_statement(Statement, Number) :-
    % Placeholder. In a real system, you would use the LLM to extract numbers.
    % Here, we simulate it with a very basic pattern.
    atom_string(Statement, StatementStr),
    split_string(StatementStr, " ", "", Words),
    member(Word, Words),
    atom_number(Word, Number).

extract_numbers_from_statement(Statement, Numbers) :-
    % Placeholder. In a real system, you would use the LLM to extract numbers.
    % Here, we simulate it with a very basic pattern.
    atom_string(Statement, StatementStr),
    split_string(StatementStr, " ", "", Words),
    findall(Number, (member(Word, Words), atom_number(Word, Number)), Numbers).

% --- Example Queries ---
% ?- validate_statement("7 is a prime number.", intent_data{primary_intent:get_information}).
% ?- validate_statement("15 is divisible by 3.", intent_data{primary_intent:solve_problem}).
% ?- validate_divisibility("20 is divisible by 4.", intent_data{primary_intent:solve_problem}).

% --- Predicates for specific number theory problems ---

% Example: Find all prime numbers within a given range
find_primes_in_range(Lower, Upper, Primes) :-
    findall(P, (between(Lower, Upper, P), prime(P)), Primes).

% Example: Check if a number is a perfect square
is_perfect_square(N) :-
    integer(N),
    N >= 0,
    Root is round(sqrt(N)),
    Root * Root =:= N.

% Example: Find the prime factorization of a number
prime_factorization(N, Factors) :-
    integer(N),
    N > 1,
    find_prime_factors(N, 2, Factors).

find_prime_factors(N, _, []) :-
    N =:= 1, !.
find_prime_factors(N, F, [F|Rest]) :-
    0 =:= N mod F, !,
    N1 is N // F,
    find_prime_factors(N1, F, Rest).
find_prime_factors(N, F, Factors) :-
    F * F < N, !,
    next_factor(F, F1),
    find_prime_factors(N, F1, Factors).
find_prime_factors(N, _, [N]).

next_factor(2, 3) :- !.
next_factor(F, F1) :-
    F1 is F + 2.

% Example usage in queries:
% find_primes_in_range(1, 20, Primes). -> Primes = [2, 3, 5, 7, 11, 13, 17, 19]
% is_perfect_square(16). -> true
% is_perfect_square(10). -> false
% prime_factorization(84, Factors). -> Factors = [2, 2, 3, 7]

% --- Predicates for validating specific theorems or properties ---

% Example: Validate a statement related to the Euclidean Algorithm
validate_euclidean_algorithm(Statement, IntentData) :-
    IntentData = intent_data{primary_intent: Intent},
    (Intent == solve_problem ; Intent == get_information),
    contains_keyword(Statement, ["greatest common divisor", "gcd", "Euclidean algorithm"]),
    extract_numbers_from_statement(Statement, [Num1, Num2]),
    gcd(Num1, Num2, GCD),
    % Check if the statement correctly describes the result of the Euclidean Algorithm
    assert_statement_contains_number(Statement, GCD).

% Example: Validate a statement about modular inverses
validate_modular_inverse(Statement, IntentData) :-
    IntentData = intent_data{primary_intent: Intent},
    (Intent == solve_problem ; Intent == get_information),
    contains_keyword(Statement, ["modular inverse", "mod"]),
    extract_numbers_from_statement(Statement, [Num, Mod]),
    mod_inverse(Num, Mod, Inverse),
    % Check if the statement correctly describes the modular inverse
    assert_statement_contains_number(Statement, Inverse).

% --- Utility Predicates ---

% Check if a statement asserts the presence of a number
assert_statement_contains_number(Statement, Number) :-
    number_string(Number, NumStr),
    contains_phrase(Statement, NumStr).

% --- Example Queries ---
% ?- validate_euclidean_algorithm("The greatest common divisor of 54 and 24 is 6.", intent_data{primary_intent:solve_problem}).
% ?- validate_modular_inverse("The modular inverse of 5 mod 7 is 3.", intent_data{primary_intent:get_information}).
