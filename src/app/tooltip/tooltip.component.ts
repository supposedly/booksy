// Made under partial guidance of a wonderful article by Netanel Basal:
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
  // TODO: Figure out what this rule means and how it applies
  // tslint:disable-next-line:directive-selector
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
        display: inline;
        background-color: #eee;
        border: 1px solid #999;
        color: #555;
        cursor: default;
        max-height: 6em;
        min-width: 20em;
        margin-left: auto;
        padding: 0.5em;
        position: absolute;
        border-radius: 6px;
        z-index: 3;
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

    const enclosedBy = this.config.host.attributes['relative'] ? 'relative' : 'absolute';
    if (enclosedBy === 'absolute') {
      this.top = `${top - height}px`;
      this.left = `${left}px`;
    } else {
      this.top = `-${height + 10}px`;
      this.left = `15px`;
    }
    this.ident = this.config.host.attributes['ident'].value;
  }

}

