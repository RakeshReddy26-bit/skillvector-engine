"use client";

import { Component } from "react";
import type { ReactNode, ErrorInfo } from "react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  message: string;
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, message: "" };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, message: error.message };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("ErrorBoundary caught:", error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback ?? (
          <div className="bg-surface border border-warn/20 rounded-xl p-8 text-center">
            <div className="text-warn text-lg font-bold mb-2">Something went wrong</div>
            <div className="font-mono text-xs text-muted">{this.state.message}</div>
            <button
              onClick={() => this.setState({ hasError: false, message: "" })}
              className="mt-4 px-6 py-2 bg-warn/10 border border-warn/20 text-warn font-mono text-xs rounded-lg hover:bg-warn/20 transition-colors"
            >
              TRY AGAIN
            </button>
          </div>
        )
      );
    }

    return this.props.children;
  }
}
