% control_agent/prolog_logic/geometry_rules.pl

% --- Geometric Knowledge ---

% Facts about geometric shapes
shape(equilateral_triangle, triangle, [side(a), side(b), side(c), angle(A), angle(B), angle(C)]).
shape(isosceles_triangle, triangle, [side(a), side(b), side(c), angle(A), angle(B), angle(C)]).
shape(scalene_triangle, triangle, [side(a), side(b), side(c), angle(A), angle(B), angle(C)]).
shape(right_triangle, triangle, [side(a), side(b), side(c), angle(A), angle(B), angle(C)]).
shape(square, quadrilateral, [side(a), side(b), side(c), side(d), angle(A), angle(B), angle(C), angle(D)]).
shape(rectangle, quadrilateral, [side(a), side(b), side(c), side(d), angle(A), angle(B), angle(C), angle(D)]).
shape(parallelogram, quadrilateral, [side(a), side(b), side(c), side(d), angle(A), angle(B), angle(C), angle(D)]).
shape(rhombus, quadrilateral, [side(a), side(b), side(c), side(d), angle(A), angle(B), angle(C), angle(D)]).
shape(trapezoid, quadrilateral, [side(a), side(b), side(c), side(d), angle(A), angle(B), angle(C), angle(D)]).
shape(circle, conic, [radius(r), center(O)]).
shape(line, basic, [point(P1), point(P2)]).
shape(point, basic, [coordinate(x), coordinate(y)]).

% Relationships between shapes
related(square, is_a, rectangle).
related(rectangle, is_a, parallelogram).
related(rhombus, is_a, parallelogram).
related(equilateral_triangle, is_a, isosceles_triangle).
related(isosceles_triangle, is_a, triangle).
related(scalene_triangle, is_a, triangle).
related(right_triangle, is_a, triangle).

% Properties of shapes
property(equilateral_triangle, equal_sides) :-
    shape(equilateral_triangle, _, Properties),
    member(side(a), Properties),
    member(side(b), Properties),
    member(side(c), Properties).

property(equilateral_triangle, equal_angles) :-
    shape(equilateral_triangle, _, Properties),
    member(angle(A), Properties),
    member(angle(B), Properties),
    member(angle(C), Properties).

property(isosceles_triangle, two_equal_sides) :-
    shape(isosceles_triangle, _, Properties),
    member(side(a), Properties),
    member(side(b), Properties),
    member(side(c), Properties).

property(right_triangle, right_angle) :-
    shape(right_triangle, _, Properties),
    member(angle(A), Properties), % Assuming angle A is the right angle
    A = 90.

property(square, four_equal_sides) :-
    shape(square, _, Properties),
    member(side(a), Properties),
    member(side(b), Properties),
    member(side(c), Properties),
    member(side(d), Properties).

property(square, four_right_angles) :-
    shape(square, _, Properties),
    member(angle(A), Properties),
    member(angle(B), Properties),
    member(angle(C), Properties),
    member(angle(D), Properties),
    A = 90, B = 90, C = 90, D = 90.

property(rectangle, opposite_sides_equal) :-
    shape(rectangle, _, Properties),
    member(side(a), Properties),
    member(side(b), Properties),
    member(side(c), Properties),
    member(side(d), Properties).

property(rectangle, four_right_angles) :-
    shape(rectangle, _, Properties),
    member(angle(A), Properties),
    member(angle(B), Properties),
    member(angle(C), Properties),
    member(angle(D), Properties),
    A = 90, B = 90, C = 90, D = 90.

property(parallelogram, opposite_sides_equal) :-
    shape(parallelogram, _, Properties),
    member(side(a), Properties),
    member(side(b), Properties),
    member(side(c), Properties),
    member(side(d), Properties).

property(parallelogram, opposite_angles_equal) :-
    shape(parallelogram, _, Properties),
    member(angle(A), Properties),
    member(angle(B), Properties),
    member(angle(C), Properties),
    member(angle(D), Properties).

property(rhombus, four_equal_sides) :-
    shape(rhombus, _, Properties),
    member(side(a), Properties),
    member(side(b), Properties),
    member(side(c), Properties),
    member(side(d), Properties).

property(circle, constant_radius) :-
    shape(circle, _, Properties),
    member(radius(r), Properties).

% Theorems and Axioms
theorem(triangle_angle_sum, 'The sum of the angles in any triangle is 180 degrees').
theorem(pythagorean, 'In a right-angled triangle, the square of the hypotenuse is equal to the sum of the squares of the other two sides').
theorem(circle_tangent, 'A tangent to a circle is perpendicular to the radius at the point of tangency').

% --- Validation Rules ---

% Example: Validate a statement about an equilateral triangle
validate_statement(Statement, IntentData) :-
    IntentData = intent_data{primary_intent: Intent},
    (Intent == solve_problem ; Intent == ask_question),
    shape(equilateral_triangle, _, _),
    contains_keyword(Statement, ["equilateral", "triangle"]),
    validate_equilateral_triangle(Statement).

validate_equilateral_triangle(Statement) :-
    ( property(equilateral_triangle, equal_sides),
      contains_keyword(Statement, ["equal", "sides"])
    ; property(equilateral_triangle, equal_angles),
      contains_keyword(Statement, ["equal", "angles"])
    ).

% Example: Validate a statement about a right triangle
validate_statement(Statement, IntentData) :-
    IntentData = intent_data{primary_intent: Intent},
    (Intent == solve_problem ; Intent == ask_question),
    shape(right_triangle, _, _),
    contains_keyword(Statement, ["right", "triangle"]),
    validate_right_triangle(Statement).

validate_right_triangle(Statement) :-
    ( property(right_triangle, right_angle),
      contains_keyword(Statement, ["right", "angle"])
    ; theorem(pythagorean, Theorem),
      contains_keyword(Statement, ["hypotenuse", "square"])
    ).

% --- Geometric Constructions and Proofs ---

% Predicates for geometric constructions and validations
collinear(A, B, C) :-
    % Check if three points A, B, and C are collinear
    A = point(X1, Y1),
    B = point(X2, Y2),
    C = point(X3, Y3),
    0 =:= (Y2 - Y1) * (X3 - X2) - (Y3 - Y2) * (X2 - X1).

perpendicular(Line1, Line2) :-
    % Check if two lines are perpendicular
    Line1 = line(point(X1, Y1), point(X2, Y2)),
    Line2 = line(point(X3, Y3), point(X4, Y4)),
    Slope1 is (Y2 - Y1) / (X2 - X1),
    Slope2 is (Y4 - Y3) / (X4 - X3),
    -1 =:= Slope1 * Slope2.

parallel(Line1, Line2) :-
    % Check if two lines are parallel
    Line1 = line(point(X1, Y1), point(X2, Y2)),
    Line2 = line(point(X3, Y3), point(X4, Y4)),
    Slope1 is (Y2 - Y1) / (X2 - X1),
    Slope2 is (Y4 - Y3) / (X4 - X3),
    Slope1 =:= Slope2.

tangent(Line, Circle) :-
    % Check if a line is tangent to a circle
    Line = line(point(X1, Y1), point(X2, Y2)),
    Circle = circle(CenterX, CenterY, Radius),
    Distance is abs((X2 - X1) * (CenterY - Y1) - (Y2 - Y1) * (CenterX - X1)) / sqrt((X2 - X1)^2 + (Y2 - Y1)^2),
    Distance =:= Radius.

% --- Utility Predicates ---

% Check if a statement mentions a certain shape
mentions_shape(Statement, Shape) :-
    contains_keyword(Statement, [Shape]).

% Check if a statement mentions a certain theorem
mentions_theorem(Statement, TheoremName) :-
    theorem(TheoremName, TheoremDescription),
    contains_keyword(Statement, [TheoremName, TheoremDescription]).

% --- Example Queries ---

% ?- validate_statement("In an equilateral triangle, all sides are equal.", intent_data{primary_intent:solve_problem}).
% ?- validate_statement("A right triangle has a right angle.", intent_data{primary_intent:ask_question}).
% ?- validate_statement("Is it true that the sum of the angles in any triangle is 180 degrees?", intent_data{primary_intent:ask_question}).

