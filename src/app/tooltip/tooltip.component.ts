// Made with partial help of a wonderful article by Netanel Basal:
// https://netbasal.com/create-advanced-components-in-angular-e0655df5dde6
import {
  Component,
  Directive,
  ElementRef,
  Inject,
  OnInit,
  ViewChild
} from '@angular/core';

@Directive({
  selector: '.tooltip-container'
})
export class TooltipContainerDirective {}

@Component({
  template: `
    <div
      class="tooltip-container"
      [ngStyle]="{top: top, left: left}" [attr.data-ident]="ident">
      <ng-content></ng-content>
    </div>
  `,
  styles: [
      `
      .tooltip-container {
        display: block;
        background-color: #eee;
        border: 1px solid #999;
        color: #555;
        width: 50em;
        padding: 0.5em;
        position: absolute;
        border-radius: 6px;
      }
    `
  ]
})
export class TooltipComponent implements OnInit {
  top: string;
  left: string;
  ident: string;
  @ViewChild(TooltipContainerDirective, {read: ElementRef}) private tooltipContainer;

  constructor(@Inject('tooltipConfig') private config) {}

  ngOnInit() {
    const {left, top} = this.config.host.getBoundingClientRect();
    const {height} = this.tooltipContainer.nativeElement.getBoundingClientRect();

    let enclosedBy = this.config.host.attributes['relative']?'relative':'absolute';
    if (enclosedBy == 'absolute') {
      this.top = `${top - height}px`;
      this.left = `${left}px`
    } else {
      this.top = `-${height + 10}px`
      this.left = `15px`
    }
    this.ident = this.config.host.attributes['ident'].value;
  }

}

