"""
CS3022 Programming Assignment - Lab 06
"What's Your Pease Number?" - Functional Programming Implementation

This program calculates the Pease Number (the most important meaningless
mathematical constant) using pure functional programming.

Steps:
1. Calculate Fibonacci Birthday Constant (FBC) = [Fibo(MM), Fibo(DD)]
2. Calculate Collatz Fibo-Birthday (CFB) = [Collatz(FBC[0]), Collatz(FBC[1]), Collatz(YYYY)]
3. Calculate Pease constant = CFB[0] + CFB[1] + CFB[2]

Author: Onur Orkut Genisel
Date: December 7, 2025
Course: CS-3022, Fall AY-25
"""

# Maybe monad implementation for error handling that wraps a value that could be None
class Maybe:
    """
    Learned about monad patterns online and adapted for this assignment
    References:
    https://python3.info/advanced/fp-patterns/maybe.html
    https://dev.to/hamzzak/mastering-monad-design-patterns-simplify-your-python-code-and-boost-efficiency-kal
    """
    
    def __init__(self, value):
        # Store the value - could be None or actual value
        self.value = value
    
    def is_nothing(self):
        # Check if we have None or a real value
        return self.value is None
    
    def bind(self, func):
        # Key monad operation - chain functions safely
        # If value is None, just return self (stay None)
        if self.is_nothing():
            return self
        # Otherwise apply the function and wrap result in Maybe
        return Maybe(func(self.value))


def create_lookup_table():
    # Initialize memoization tables for Fibonacci and Collatz
    return {
        'fibo': {0: 0, 1: 1},
        'collatz': {1: 0}
    }


def make_fibo_calculator(lookup_table):
    # Using closure pattern to keep lookup table in scope
    def fibo(n):
        if n < 0:
            raise ValueError("Fibonacci input must be non-negative")
        
        # Check if we already calculated this
        if n in lookup_table['fibo']:
            return lookup_table['fibo'][n]
        
        # Recursively calculate and store
        result = fibo(n - 1) + fibo(n - 2)
        lookup_table['fibo'][n] = result
        #print(f"Debug: Calculated fibo({n}) = {result}")
        return result
    
    return fibo


def make_collatz_calculator(lookup_table):
    # Using closure pattern for Collatz sequence calculator
    def collatz(n, max_steps=1500):
        # Base case - we've reached 1
        if n == 1:
            return 0
        
        # Check memoization table first
        if n in lookup_table['collatz']:
            return lookup_table['collatz'][n]
        
        # Safety check - prevent infinite loops
        # Not sure what's a good limit, 1500 seems reasonable
        if max_steps <= 0:
            return None
        
        # Apply Collatz rules
        # If the number is even, divide by two
        # If the number is odd, multiply by three and add one
        next_n = n // 2 if n % 2 == 0 else 3 * n + 1
        # Repeat until you get to 1
        next_steps = collatz(next_n, max_steps - 1)
        
        if next_steps is None:
            return None
        
        result = 1 + next_steps
        lookup_table['collatz'][n] = result
        return result
    
    return collatz


def collatz_convergence_check(n, collatz_func):
    # Helper function to check if a number converges in Collatz sequence
    # Returns True if it converges, False if it doesn't
    steps = collatz_func(n)
    return steps is not None


def calculate_pease_number(month, day, year, fibo_func, collatz_func):
    # Main calculation function for Pease number
    
    # Step 1: Calculate Fibonacci Birthday Constant (FBC)
    fibo_mm = fibo_func(month)
    fibo_dd = fibo_func(day)
    
    # Helper function for safe Collatz calculation
    def safe_collatz(n):
        if not collatz_convergence_check(n, collatz_func):
            return None
        return collatz_func(n)
    
    # Try using Maybe monad to chain operations
    # This should handle errors automatically if Collatz doesn't converge
    
    # Start with fibo_mm, wrap in Maybe, then apply safe_collatz
    cfb_0_maybe = Maybe(fibo_mm)
    cfb_0_maybe = cfb_0_maybe.bind(safe_collatz)
    
    # Same for fibo_dd
    cfb_1_maybe = Maybe(fibo_dd)
    cfb_1_maybe = cfb_1_maybe.bind(safe_collatz)
    
    # And for the year
    cfb_2_maybe = Maybe(year)
    cfb_2_maybe = cfb_2_maybe.bind(safe_collatz)
    
    # Check if any of the Collatz calculations failed to converge
    if cfb_0_maybe.is_nothing():
        return f"Error: Fibo({month})={fibo_mm} does not converge", None
    if cfb_1_maybe.is_nothing():
        return f"Error: Fibo({day})={fibo_dd} does not converge", None
    if cfb_2_maybe.is_nothing():
        return f"Error: Year {year} does not converge", None
    
    # Extract the values from Maybe and calculate Pease number
    cfb_list = [cfb_0_maybe.value, cfb_1_maybe.value, cfb_2_maybe.value]
    pease_constant = sum(cfb_list)
    
    # Return None for error and a dict with results
    return None, {
        "FBC": [fibo_mm, fibo_dd],
        "CFB": cfb_list,
        "Pease_Number": pease_constant
    }


def user_interaction_loop(fibo_func, collatz_func):
    # Objective 1: User prompted to input a Month and a Year
    try:
        user_input = input("\nEnter Month Day Year (MM DD YYYY) or press Enter to quit: ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nProgram terminated.")
        return
    
    # Empty input means quit
    if not user_input:
        return
    
    # Parse the input
    parts = user_input.split()
    if len(parts) != 3:
        print("Error: Please enter exactly 3 values (MM DD YYYY)")
        return user_interaction_loop(fibo_func, collatz_func)
    
    # Convert to integers
    try:
        month, day, year = int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError:
        print("Error: Please enter valid integers")
        return user_interaction_loop(fibo_func, collatz_func)
    
    # Basic validation
    # Meaningless info: oldest living person, Ethel Caterham, born in 1909
    # Another meaningless info: at the age of 110, Caterham survived COVID-19.
    if not (1 <= month <= 12 and 1 <= day <= 31 and year >= 1909):
        print("Error: Invalid date values")
        return user_interaction_loop(fibo_func, collatz_func)
    
    # Objective 2: Pease number is calculated and displayed to the screen
    error, results = calculate_pease_number(month, day, year, fibo_func, collatz_func)
    
    if error:
        print(error)
    elif results:
        print(f"\nResults for {month}/{day}/{year}:")
        print(f"  FBC = {results['FBC']}")
        print(f"  CFB = {results['CFB']}")
        print(f"  Pease Number = {results['Pease_Number']}")
    
    # Objective 3: Go to step 1
        return user_interaction_loop(fibo_func, collatz_func)


def main():
    # Main entry point
    print("Pease Number Calculator")
    
    # Set up the memoization table and create calculator functions
    lookup_table = create_lookup_table()
    fibo_calculator = make_fibo_calculator(lookup_table)
    collatz_calculator = make_collatz_calculator(lookup_table)
    
    # Show example calculation from the assignment
    print("\nExample Birthday: 04 10 1982")
    error, results = calculate_pease_number(4, 10, 1982, fibo_calculator, collatz_calculator)
    
    if results:
        print(f"  FBC = {results['FBC']}")
        print(f"  CFB = {results['CFB']}")
        print(f"  Pease Number = {results['Pease_Number']}")
    
    # Start the interactive loop
    user_interaction_loop(fibo_calculator, collatz_calculator)


if __name__ == "__main__":
    main()
