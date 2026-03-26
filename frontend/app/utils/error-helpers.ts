import { ApiError } from "@/services/api-client";

export function getErrorMessage(err: unknown, fallback: string): string {
  if (err instanceof ApiError) {
    if (typeof err.body === "string" && err.body.trim()) {
      return err.body;
    }

    if (err.body && typeof err.body === "object" && "detail" in err.body) {
      const detail = err.body.detail;

      if (typeof detail === "string" && detail.trim()) {
        return detail;
      }

      if (Array.isArray(detail)) {
        const messages = detail
          .map((item) => {
            if (!item || typeof item !== "object") {
              return null;
            }

            const path =
              "loc" in item && Array.isArray(item.loc)
                ? item.loc
                    .filter(
                      (part: unknown): part is string | number =>
                        typeof part === "string" || typeof part === "number"
                    )
                    .join(".")
                : "";
            const message =
              "msg" in item && typeof item.msg === "string" ? item.msg : "";

            if (!message) {
              return null;
            }

            return path ? `${path}: ${message}` : message;
          })
          .filter((message): message is string => Boolean(message));

        if (messages.length > 0) {
          return messages.join(", ");
        }
      }
    }
  }

  if (err instanceof Error && err.message.trim()) {
    return err.message;
  }

  return fallback;
}
