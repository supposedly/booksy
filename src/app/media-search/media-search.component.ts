import { Component } from '@angular/core';

@Component({
  selector: 'app-media-search',
  template: `
    <media-suggestion heading="Based on your most-recent checkout:"></media-suggestion>
    <media-search-bar all-items heading="Search for items:"></media-search-bar>
  `,
  styleUrls: ['./media-search.component.css']
})
export class MediaSearchComponent {}

