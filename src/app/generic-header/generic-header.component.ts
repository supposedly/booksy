import { Component, Input } from '@angular/core';

@Component({
  selector: 'generic-header',
  templateUrl: './generic-header.component.html',
  styleUrls: ['./generic-header.component.css']
})
export class GenericHeaderComponent {
  @Input() buttons: any;
  @Input() inbetween: string;
}
