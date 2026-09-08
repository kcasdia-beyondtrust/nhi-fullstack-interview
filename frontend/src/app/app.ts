import { Component, inject, signal, OnInit } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';

interface Greeting {
  message: string;
}

@Component({
  imports: [],
  selector: 'app-root',
  styleUrl: './app.css',
  templateUrl: './app.html',
})
export class App implements OnInit {
  private readonly http = inject(HttpClient);

  protected readonly greeting = signal<string | null>(null);
  protected readonly error = signal<string | null>(null);
  protected readonly loading = signal(true);

  ngOnInit(): void {
    // '/api' is proxied to the Flask app on :5000 by proxy.conf.json, so this
    // stays same-origin and works unchanged behind the VM's HTTPS proxy.
    this.http.get<Greeting>('/api/hello').subscribe({
      next: (greeting) => {
        this.greeting.set(greeting.message);
        this.loading.set(false);
      },
      error: (err: HttpErrorResponse) => {
        this.error.set(
          err.status === 0
            ? 'Could not reach the API. Is the Flask app running on port 5000?'
            : `API returned ${err.status}: ${err.error?.error ?? err.message}`,
        );
        this.loading.set(false);
      },
    });
  }
}
