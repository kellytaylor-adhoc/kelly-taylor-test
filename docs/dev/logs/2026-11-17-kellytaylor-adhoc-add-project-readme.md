# Session Log

## Objective

Add and improve the project README.

## Related

- Branch: `kellytaylor-adhoc-add-project-readme`

## Work Completed

- Updated the README with the live site URL and deployment instructions.
- Corrected the local setup steps to copy generated CMS data into the frontend's static data directory.

## Decisions Made

- Documented the frontend as a static application that reads `public/companies.json`; the FastAPI server is optional for normal UI use.
- Kept the existing API endpoint documentation because it is useful for local integrations.

## Lessons Learned

- The README setup steps must include copying backend data into the frontend public directory before the Vite development server can render real results.
