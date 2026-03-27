import { apiClient } from "@/services/api-client";
import type { User } from "@/services/types";

export async function getCurrentUser(token: string): Promise<User> {
  return apiClient<User>("/users/me", {}, token);
}

export async function getUsers(token: string): Promise<User[]> {
  return apiClient<User[]>("/users/", {}, token);
}
