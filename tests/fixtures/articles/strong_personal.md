---
title: I spent six months writing a programming language nobody asked for
subtitle: What building a toy language taught me about the ones I use daily
audience: developers curious about language internals
article_type: personal-experience
ai_assistance: none
---

# I spent six months writing a programming language nobody asked for
**What building a toy language taught me about the ones I use daily**

Last November I opened an empty editor and decided to build a programming
language. Not a DSL, not a transpiler — a real language with a parser, a
type checker, and a bytecode VM. Six months later I have 4,000 lines of
Rust, eleven users (I know all of them), and a completely different
relationship with every language I use.

## The moment I got humbled

Week three, I implemented closures and felt invincible. Then my friend
wrote this and my VM fell over:

```
fn counter() { let x = 0; return fn() { x = x + 1; x } }
```

Upvalues. I had closures that captured values but not *mutable* upvalues,
which meant my language silently gave every closure its own copy. Three
evenings of confusion later, I finally understood what "closures capture
the environment" actually means — something I'd confidently explained in
code reviews for years.

## What I got wrong about performance

I assumed bytecode would be fast enough. My first interpreter ran FizzBuzz
in 40ms. Forty. I profiled, found the constant pool lookup in the hot loop,
switched to inline caching, and got it to 2ms. Then I read the LuaJIT
papers properly and realized my "optimization" was their 1995 baseline.
The gap between "works" and "fast" was full of things I thought I knew.

## What it changed for me

I read language error messages differently now — I know exactly why "expected
expression, found 'else'" happens, because I wrote that message badly myself
and users complained. I stopped taking garbage collection for granted after
writing the naive mark-sweep that froze my REPL for 300ms every few seconds.
When I review PRs that touch our parser at work, I catch things I simply
could not see before.

## What I'd tell you if you want to try this

Do it, but smaller than you think. My mistake was starting with the type
system; I should have shipped the calculator first. The craft payoff is
real, but the bigger payoff is humility: every language I use now is a
thousand decisions I can finally see.
