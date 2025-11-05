import Cookies from "js-cookie";
import { StateStorage } from "zustand/middleware";

export const cookieStorage: StateStorage = {
  getItem: (name: string): string | null => {
    return Cookies.get(name) || null;
  },
  setItem: (name: string, value: string): void => {
    Cookies.set(name, value, { expires: 7 }); // 7 days
  },
  removeItem: (name: string): void => {
    Cookies.remove(name);
  },
};
