# Code Restrictions

The following code restrictions are necessary to ensure that the functions inside
gettsim can be vectorized automatically. The code restrictions are checked and throw an
error if violated.

## If-Else Conditions

1. For a single assignment that depends on one condition, prefer a ternary expression.
   Vectorization converts it to `xnp.where`, just as it does for the equivalent if /
   else block:

   ```python
   out = 1 if x > 1 else 0
   ```

   Use statement `if` / `elif` / `else` for nested or multi-branch logic where a ternary
   would hurt readability.

1. Code inside an if / elif / else block can only perform one operation. For example,
   the following is allowed:

   ```python
   if x > 1:
       out = 1
   else:
       out = 0
   ```

   while

   ```python
   if x > 1:
       flag = True
       out = 1
   else:
       out = 0
   ```

   is not allowed since the code inside the if block performs two operations.

1. There cannot be a return statement inside a single if-condition. For example, the
   following is allowed:

   ```python
   if x > 1:
       return 1
   else:
       return 0
   ```

   or

   ```python
   if x > 1:
       out = 1
   else:
       out = 0
   return out
   ```

   while

   ```python
   out = 0
   if x > 1:
       return 1
   return out
   ```

   is not allowed.

1. Only certain operations can be performed in the body of an if / elif / else
   condition. For example, the following operations are allowed:

   - Assigning a variable (e.g. `out = 1`)
   - Returning a value (e.g. `return 1`)
   - One-line if-else conditions (e.g. `out = 1 if x > 1 else 0`)
   - Nested if-elif-else conditions

## Function Calls

This is a list of restrictions applying to functions from the base and math modules.

1. The following functions can only be called with iterable arguments:

   - `sum`
   - `any`
   - `all`

   For example the following is allowed:

   ```python
   any([True, False, False])
   ```

   while

   ```python
   any(True, False, False)
   ```

   ```
   is not allowed.

   ```

1. The following functions can only be called with **two** arguments or **one** iterable
   argument. For example the following is allowed:

   ```python
   min([1, 2, 3])
   ```

   and

   ```python
   min(left, right)
   ```

   while

   ```python
   min(1, 2, 3)
   ```

   or

   ```python
   min(left, middle, right)
   ```

   is not allowed.
