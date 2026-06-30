import * as React from "react";
import { cn } from "@/lib/utils";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost";
};

export function Button({ className, variant = "primary", ...props }: ButtonProps) {
  const styles = {
    primary: "bg-primary text-primary-foreground hover:bg-teal-700",
    secondary: "bg-white text-slate-900 border hover:bg-slate-50",
    ghost: "text-slate-700 hover:bg-slate-100"
  };
  return (
    <button
      className={cn(
        "inline-flex h-10 items-center justify-center rounded-md px-4 text-sm font-medium transition disabled:cursor-not-allowed disabled:opacity-60",
        styles[variant],
        className
      )}
      {...props}
    />
  );
}
