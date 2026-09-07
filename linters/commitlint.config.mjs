export default {
  extends: ["@commitlint/config-conventional"],
  plugins: [
    {
      rules: {
        "subject-pt-br": ({ subject }) => {
          if (!subject) return [true];
          const englishWords = [
            /\badd\b/i, /\badding\b/i, /\badded\b/i,
            /\bupdate\b/i, /\bupdating\b/i, /\bupdated\b/i,
            /\bremove\b/i, /\bremoving\b/i, /\bremoved\b/i,
            /\brefine\b/i, /\brefining\b/i, /\brefined\b/i,
            /\btune\b/i, /\btuning\b/i, /\btuned\b/i,
            /\bimplement\b/i, /\bimplementing\b/i, /\bimplemented\b/i,
            /\balign\b/i, /\baligning\b/i, /\baligned\b/i,
            /\bfix\b/i, /\bfixing\b/i, /\bfixed\b/i,
            /\btest\b/i, /\btesting\b/i, /\btested\b/i,
            /\bclean\b/i, /\bcleaning\b/i, /\bcleaned\b/i,
            /\ballow\b/i, /\ballowing\b/i, /\ballowed\b/i,
            /\bchange\b/i, /\bchanging\b/i, /\bchanged\b/i,
          ];
          const found = englishWords.find((regex) => regex.test(subject));
          if (found) {
            return [
              false,
              `O assunto do commit deve ser escrito em Portugues (PT-BR). Palavra em ingles detectada: "${subject}"`,
            ];
          }
          return [true];
        },
      },
    },
  ],
  rules: {
    "subject-pt-br": [2, "always"],
    "type-enum": [
      2,
      "always",
      [
        "build",
        "chore",
        "ci",
        "docs",
        "feat",
        "fix",
        "perf",
        "qa",
        "refactor",
        "revert",
        "style",
        "test",
      ],
    ],
    "scope-enum": [
      2,
      "always",
      [
        "all",
        "app",
        "cli",
        "config",
        "deps",
        "domain",
        "infra",
        "linters",
        "repo",
        "scripts",
        "test",
      ],
    ],
    "type-case": [2, "always", "lower-case"],
    "type-empty": [2, "never"],
    "scope-empty": [2, "never"],
    "subject-empty": [2, "never"],
    "subject-case": [0],
    "body-leading-blank": [2, "always"],
    "body-empty": [2, "never"],
    "header-max-length": [2, "always", 100],
  },
};
